from src.suma import sum
from src.resta import subtraction
from src.multiplication import multiply
from src.division import divide

def main(): 
  a = float(input("Ingrese el primer número: "))
  operation = input("Ingrese la operación (+, -, *, /): ")
  b = float(input("Ingrese el segundo número: "))

  message = "El resultado es: "

  if operation == "+":
      message += str(int(sum(a, b)))
  elif operation == "-":
      message += str(int(subtraction(a, b)))
  elif operation == "*":
      message += str(int(multiply(a, b)))
  elif operation == "/":
      if b == 0:
          message = "Error: No se puede dividir por cero"
      else:
          message += str(int(divide(a, b)))
  else:
      message = "Operación no válida"

  print(message)


if __name__ == "__main__":
  main()
