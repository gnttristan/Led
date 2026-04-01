import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 300, 1000)
y = (0.78
     - 0.32/(1 + np.exp(-(x-75)/9))
     + 0.12/(1 + np.exp(-(x-225)/10)))

plt.plot(x, y)
plt.xlim(0, 300)
plt.show()