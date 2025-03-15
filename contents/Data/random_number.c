#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h>

double getRandomNumber() 
{
    double randomNumber = (float) rand() / RAND_MAX;
    return randomNumber;
}

void printArray(double arr[], int size)
{
    //int size = sizeof(arr) / sizeof(arr[0]);
    printf("There are %d elements in the array.\n", size);

    for(int i = 0; i < size; i++)
    {
        printf("arr[%d]: %d\n", i, arr[i]);
    }
}

int main()
{
    srand(time(NULL));
    time_t start = time(NULL);

    int random_number = rand(); // get a random number
    double numbers[random_number]; // generate an array of doubles of that size.
    printf("Making an array of size: %d\n", random_number);

    for (int i = 0; i < random_number; i++)
    {
        numbers[i] = getRandomNumber();
    }

    printArray(numbers, random_number);

    time_t end = time(NULL);
    Sleep(2000);
    double timeDiff = difftime(end, start);
    printf("Total time for calculations: %.0f\n", timeDiff);
    return 0;
}