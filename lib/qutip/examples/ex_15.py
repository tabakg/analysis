#
# Energy spectrum of three coupled qubits.
#
from qutip import *
from pylab import *


def compute(w1list, w2, w3, g12, g13):
    # Pre-compute operators for the hamiltonian

    # qubit 1 operators
    sz1 = tensor(sigmaz(), qeye(2), qeye(2))
    sx1 = tensor(sigmax(), qeye(2), qeye(2))

    # qubit 2 operators
    sz2 = tensor(qeye(2), sigmaz(), qeye(2))
    sx2 = tensor(qeye(2), sigmax(), qeye(2))

    # qubit 3 operators
    sz3 = tensor(qeye(2), qeye(2), sigmaz())
    sx3 = tensor(qeye(2), qeye(2), sigmax())

    # preallocate output array
    evals_mat = zeros((len(w1list), 2 * 2 * 2))
    for idx, w1 in enumerate(w1list):

        # evaluate the Hamiltonian
        H = w1 * sz1 + w2 * sz2 + w3 * sz3 + g12 * sx1 * sx2 + g13 * sx1 * sx3

        # find the energy eigenvalues and vectors of the composite system
        evals, evecs = H.eigenstates()
        evals_mat[idx, :] = evals

    return evals_mat


def run():
    #
    # set up the calculation
    #
    w1 = 1.0 * 2 * pi   # atom 1 frequency: sweep this one
    w2 = 0.9 * 2 * pi   # atom 2 frequency
    w3 = 1.1 * 2 * pi   # atom 3 frequency
    g12 = 0.05 * 2 * pi   # atom1-atom2 coupling strength
    g13 = 0.05 * 2 * pi   # atom1-atom3 coupling strength

    # range of qubit 1 frequencies
    w1list = linspace(0.75, 1.25, 50) * 2 * pi

    # run computation
    evals_mat = compute(w1list, w2, w3, g12, g13)

    #
    # plot the energy eigenvalues
    #
    figure()
    colors = ['b', 'r', 'g']  # list of colors for plotting
    for n in [1, 2, 3]:
        plot(w1list / (2 * pi), (evals_mat[:, n] - evals_mat[:, 0]) / (2 * pi),
             colors[n - 1], lw=2)

    xlabel('Energy Splitting of Qubit 1')
    ylabel('Eigenenergies')
    title('Energy Spectrum of Three Coupled Qubits')
    show()
    close()


if __name__ == "__main__":
    run()
