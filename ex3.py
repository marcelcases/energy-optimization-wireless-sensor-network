"""
Project 1 - Problem 3
"""

########################################################
######## X-MAC: Trade_off Energy with Delay using GT
########################################################
# Radio subsystem varaible definition

P     = 32.            # Payload [byte]
R     = 31.25          # CC2420 Radio Rate [kbyte/s = Byte/ms]
D     = 8              # number of levels
C     = 5              # neighbors size (connectivity)
N     = C*D**2          # number of nodes
#### BE CAREFUL:  Times are in milliseconds (ms)
Lmax  = 5000.          # Maximal allowed Delay (ms)
Emax  = 1.            # MAximal Energy Budjet (J)

L_pbl = 4.             # preamble length [byte]
L_hdr = 9. + L_pbl     # header length [byte]
L_ack = 9. + L_pbl     # ACK length [byte]
L_ps  = 5. + L_pbl     # preamble strobe length [byte]

Tal  = 0.95            # ack listen period [ms]
Thdr = L_hdr/R         # header transmission duration [ms]
Tack = L_ack/R         # ACK transmission duration [ms]
Tps  = L_ps/R          # preamble strobe transmission duration [ms]
Tcw  = 15*0.62         # Contention window size [ms]
Tcs  = 2.60            # Time [ms] to turn the radio into TX and probe the channel (carrier sense)
Tdata = Thdr + P/R + Tack # data packet transmission duration [ms]

### Sampling frequency
# Fs   = 1.0/(60*30*1000)    # e.g. Min traffic rate 1 pkt/half_hour = 1/(60*30*1000) pk/ms
Fs = 1./(15*60*1000) #default

# Sleep period: Parameter Bounds
Tw_max  = 500.       # Maximum Duration of Tw in ms
Tw_min  = 100.       # Minimum Duration of Tw in ms


def Nd(d):
    if d == 0:
        return 1
    return (2*d - 1)*C

def Id(d):
    if d == 0:
        return C
    elif d == D:
        return 0
    return (2*d + 1)/(2*d - 1)
    # return Nd(d+1)/Nd(d)

def Fout(d):
    if d == D:
        return Fs
    return Fs*(D**2 - d**2 + 2*d - 1)/(2*d - 1)
    # return FI(d)+Fs

def FI(d):
    if d == 0:
        return Fs*C*D**2
    return Fs*(D**2 - d**2)/(2*d - 1)
    # return Id(d)*Fout(d+1)

def FB(d):
    return (C - Id(d))*Fout(d)

def Etx(d, Tw):
    return (Tcs + Tal + Ttx(Tw))*Fout(d)

def Ttx(Tw):
    return (Tw/2 + Tack + Tdata)


################
# Optimization #
################

from scipy.optimize import minimize
import numpy as np

d = 1 # first ring
α1 = Tcs + Tal + (3/2)*Tps*((Tps + Tal)/2 + Tack + Tdata)*FB(d)
α2 = Fout(d)/2
α3 = ((Tps + Tal)/2 + Tcs + Tal + Tack + Tdata)*Fout(d) + ((3/2)*Tps + Tack + Tdata)*FI(d) + (3/4)*Tps*FB(d)

d = D # last ring
β1 = sum(1/2 for i in range(1, d+1))
β2 = sum(Tcw/2 + Tdata for i in range(1, d+1))

E = lambda Tw: α1/Tw + α2*Tw + α3
L = lambda Tw: β1*Tw + β2

Eworst = 0.05
Lworst = 2000

def solve():
    # Objective function
    fun = lambda E1, L1: -np.log(Eworst-E1) -np.log(Lworst-L1)

    # constraints
    cons = ({'type': 'ineq', 'fun': lambda Tw: Eworst - E(Tw)},
            {'type': 'ineq', 'fun': lambda E1, Tw: E1 - E(Tw)},
            {'type': 'ineq', 'fun': lambda Tw: Lworst - L(Tw)},
            {'type': 'ineq', 'fun': lambda L1, Tw: L1 - L(Tw)},
            {'type': 'ineq', 'fun': lambda Tw: Tw - Tw_min},
            {'type': 'ineq', 'fun': lambda Tw: 1/4 - Id(0)*Etx(1,Tw)}
            )

    # bounds, if any, e.g. x1 and x2 have to be positive
    bnds = ((None, None), )*1

    # initial guesses
    x0 = 0

    # Method SLSQP uses Sequential Least SQuares Programming to minimize a function 
    # of several variables with any combination of bounds, equality and inequality constraints. 
    res = minimize(fun, x0, method='SLSQP', bounds=bnds, constraints=cons)
    print('\n',res)
    # print("optimal value p*", res.fun)
    # print("optimal var: x1 = ", res.x[0], " x2 = ", res.x[1])

# solve()

#########
# Plots #
#########

import matplotlib.pyplot as plt
import numpy as np
import random

# Tw = np.linspace(Tw_min/1000,Tw_max/1000,100)
Tw = np.linspace(50,300,100)
# Tw_linsp = np.linspace(70,500,100)
# Tw_linsp = np.linspace(70/1000,500/1000,100)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
# ax.spines['left'].set_position('center')
# ax.spines['bottom'].set_position('zero')
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
# ax.xaxis.set_ticks_position('bottom')
# ax.yaxis.set_ticks_position('left')

def plotNBS():
    d = 1 # first ring
    α1 = Tcs + Tal + (3/2)*Tps*((Tps + Tal)/2 + Tack + Tdata)*FB(d)
    α2 = Fout(d)/2
    α3 = ((Tps + Tal)/2 + Tcs + Tal + Tack + Tdata)*Fout(d) + ((3/2)*Tps + Tack + Tdata)*FI(d) + (3/4)*Tps*FB(d)

    d = D # last ring
    β1 = sum(1/2 for i in range(1, d+1))
    β2 = sum(Tcw/2 + Tdata for i in range(1, d+1))

    # print(α1, α2, α3, β1, β2)

    E = lambda Tw: α1/Tw + α2*Tw + α3
    L = lambda Tw: β1*Tw + β2

    # print(E(0.1), E(0.5))
    # Txprint=0.03
    # print(Txprint, E(Txprint), L(Txprint), E(L(Txprint)), L(E(Txprint)))

    # Plot Energy(Tw)
    # plt.plot(Tw, E(Tw), random.choice("bgrcmyk"), label='Energy E(Tw) for Fs=' + str(Fs)[:4] + str(Fs)[-4:])

    # Plot Delay(Energy)
    plt.plot(E(Tw), L(Tw), color='b', label='Delay=f(Energy) for Fs(' + str(15) + 'min) = ' + str(Fs)[:4] + str(Fs)[-4:])
    ax.scatter(0.04155, 431.1, color='y', label='Tradeoff Point for Lmax=500')
    ax.scatter(0.03467, 529.0, color='g', label='Tradeoff Point for Lmax=750')
    ax.scatter(0.03114, 610.2, color='r', label='Tradeoff Point for Lmax=1000')
    ax.scatter(0.02869, 687.2, color='c', label='Tradeoff Point for Lmax=2500')
    ax.scatter(0.02676, 776.7, color='m', label='Tradeoff Point for Lmax=5000')

    plt.xlabel("E(Tw)")
    plt.ylabel("L(Tw)")

    plt.legend(loc='upper right')
    plt.show()

plotNBS()
