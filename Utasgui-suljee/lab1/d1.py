import math
import numpy as np
import matplotlib.pyplot as plt

def task1():
    total = sum(range(1, 101))
    print("1-100 хүртэлх тооны нийлбэр:", total)

def task2():
    numbers = []
    for i in range(8):
        num = int(input(f"{i+1}-р тоог оруулна уу: "))
        numbers.append(num)
    print("Оруулсан 8 тоо:", numbers)

def task3():
    r = float(input("Тойргийн радиус оруулна уу: "))
    length = 2 * math.pi * r
    area = math.pi * r**2
    print(f"Тойргийн урт = {length}")
    print(f"Тойргийн талбай = {area}")

def task4():
    t = np.linspace(0, 0.01, 1000)
    fc = 200      # carrier давтамж
    fm = 20       # message давтамж
    m = 0.5       # модуляцын гүн

    message = np.sin(2*np.pi*fm*t)
    carrier = np.sin(2*np.pi*fc*t)
    modulated = (1 + m*message) * carrier

    plt.figure(figsize=(10,6))
    plt.subplot(3,1,1)
    plt.plot(t, message)
    plt.title("Message signal m(t) = sin(2πfmt)")

    plt.subplot(3,1,2)
    plt.plot(t, carrier)
    plt.title("Carrier signal c(t) = sin(2πfct)")

    plt.subplot(3,1,3)
    plt.plot(t, modulated)
    plt.title("AM Modulated signal y(t)")

    plt.tight_layout()
    plt.show()

def task5():
    x = np.linspace(0, 2*np.pi, 500)
    y = np.cos(x)
    plt.figure()
    plt.plot(x, y)
    plt.title("y = cos(x)")
    plt.xlabel("x")
    plt.ylabel("cos(x)")
    plt.grid(True)
    plt.show()

def task6():
    students = [
        "Dulguun, 101",
        "hashaa ,102",
        "Jangar, 103",
        "amaraa, 104"
    ]
    with open("students.txt", "w", encoding="utf-8") as f:
        for s in students:
            f.write(s + "\n")

    print("\nФайлд бичсэн оюутны жагсаалт:")
    with open("students.txt", "r", encoding="utf-8") as f:
        for line in f:
            print(line.strip())

while True:
    print("\n----- Даалгавap сонголт-----")
    print("1. 1–100 хүртэлх тооны нийлбэр олох")
    print("2. Гараас 8 тоо оруулж хэвлэх")
    print("3. Тойргийн урт ба талбай олох")
    print("4. y = sin(x) дохионы модуляц ба график")
    print("5. y = cos(x) дохионы график")
    print("6. Оюутны нэр, кодыг файлд бичиж унших")
    print("0. Гарах")

    choice = input("Даалгаврын дугаар сонгоно уу: ")

    if choice == "1":
        task1()
    elif choice == "2":
        task2()
    elif choice == "3":
        task3()
    elif choice == "4":
        task4()
    elif choice == "5":
        task5()
    elif choice == "6":
        task6()
    elif choice == "0":
        print("Програм дууслаа.")
        break
    else:
        print("Буруу сонголт хийлээ, дахин оролдоно уу.")
