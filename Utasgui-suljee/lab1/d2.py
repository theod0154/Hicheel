
import numpy as np
import matplotlib.pyplot as plt

# Хугацааны интервал (0–2 хүртэл, 0.01 алхамтай)
t = np.arange(0, 2, 0.01)

# Давтамж
f = 10**6   # 1 MHz

# 1. y1 = Sin(2π*f*t)
y1 = np.sin(2 * np.pi * f * t)

# 2. y2 = (1/3) * Sin(2π*(3f)*t)
y2 = (1/3) * np.sin(2 * np.pi * 3 * f * t)

# 3. y3 = y1 + y2
y3 = y1 + y2

# 4. y4 = (4/π) * (Sin(2π*f*t) + (1/3)*Sin(2π*3f*t))
y4 = (4/np.pi) * (np.sin(2*np.pi*f*t) + (1/3)*np.sin(2*np.pi*3*f*t))

# 5. x = Fourier series up to 5th term
x = (4/np.pi) * (np.sin(2*np.pi*f*t) + 
                 (1/3)*np.sin(2*np.pi*3*f*t) + 
                 (1/5)*np.sin(2*np.pi*5*f*t))

# 6. x1 = Fourier series up to 7th term
x1 = (4/np.pi) * (np.sin(2*np.pi*f*t) + 
                  (1/3)*np.sin(2*np.pi*3*f*t) + 
                  (1/5)*np.sin(2*np.pi*5*f*t) +
                  (1/7)*np.sin(2*np.pi*7*f*t))


plt.figure(figsize=(12,10))

plt.subplot(3,2,1)
plt.plot(t, y1)
plt.title("y1 = Sin(2π f t)")

plt.subplot(3,2,2)
plt.plot(t, y2)
plt.title("y2 = (1/3) Sin(2π (3f) t)")

plt.subplot(3,2,3)
plt.plot(t, y3)
plt.title("y3 = y1 + y2")

plt.subplot(3,2,4)
plt.plot(t, y4)
plt.title("y4 = (4/π)(Sin(2π f t)+(1/3)Sin(2π 3f t))")

plt.subplot(3,2,5)
plt.plot(t, x)
plt.title("x = Fourier series up to 5th term")

plt.subplot(3,2,6)
plt.plot(t, x1)
plt.title("x1 = Fourier series up to 7th term")

plt.tight_layout()
plt.show()
