data = []
totalcolumn = 0
totalrow = 0
def main():
    global data, totalcolumn, totalrow
 
    file = input("Enter filename: ")
 
    for line in open(file + ".txt"):
        items = line.split(' ')
        # create list with all numbers
        a = list(map(int, line.split()))
 
 
        totalrow = len(a)
        aInt = []
        for x in a:
            aInt.append(int(x))
        data.append(aInt)
    totalcolumn = len(data)
   
 
    if totalcolumn == totalrow:
        for x in range(totalcolumn):
            row = (calculateRow(x))
            col = (calculateColumn(x))
            diag = (calculateDiagonal())
            inv = calculateInverseDiagonal()
            if not row == col == diag == inv:
                with open(file + "_output.txt", "w") as f:
                    f.write("The sums of the row, column and diagonals are not equal\n")
                    f.write("Row: " + str(row) + "\n")
                    f.write("Column: " + str(col) + "\n")
                    f.write("Diagonal: " + str(diag) + "\n")
                    f.write("Inverse: "+ str(inv))
                    
                return False

    with open(file + "_output.txt", "w") as f:
        f.write("The sums of the row, column and diagonals are equal\n")
        f.write("Row: " + str(row) + "\n")
        f.write("Column: " + str(col) + "\n")
        f.write("Diagonal: " + str(diag) + "\n")
        f.write("Inverse: "+ str(inv) + "\n")
        f.write("This is a magic square")

    return True  
 
 
def calculateRow(x):
    global data
    sum = 0
    for x in data[x]:
        sum = sum+x
    return sum
 
def calculateColumn(y):
    global data
    sum = 0
    for x in data:
        sum = sum+x[y]
    return sum
 
 
def calculateDiagonal():
    global data,totalcolumn
    sum = 0
    for x in range(totalcolumn):
        sum = sum+data[x][x]
    return sum

def calculateInverseDiagonal():
    global data,totalcolumn
    sum = 0
    for x in range(totalcolumn):
        sum = sum+data[x][(totalcolumn-1) - x]
    return sum
 
main()