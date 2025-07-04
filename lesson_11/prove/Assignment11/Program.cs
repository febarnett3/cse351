﻿// 4. Meets Requirments: Implements 10 threads and a queue to speed up program
using System.Diagnostics;

namespace assignment11;

public class Assignment11
{
    private const long START_NUMBER = 10_000_000_000;
    private const int RANGE_COUNT = 1_000_000;

    private static bool IsPrime(long n)
    {
        if (n <= 3) return n > 1;
        if (n % 2 == 0 || n % 3 == 0) return false;

        for (long i = 5; i * i <= n; i = i + 6)
        {
            if (n % i == 0 || n % (i + 2) == 0)
                return false;
        }
        return true;
    }

    public static void Main(string[] args)
    {
        // Use local variables for counting since we are in a single thread.
        int numbersProcessed = 0;
        int primeCount = 0;
        
        object lockObj = new object();
        Queue<long> primeQueue = new Queue<long>();
        Thread[] threads = new Thread[10];

        Console.WriteLine("Prime numbers found:");

        var stopwatch = Stopwatch.StartNew();
        
        for (long i = START_NUMBER; i < START_NUMBER + RANGE_COUNT; i++)
        {
            primeQueue.Enqueue(i);
        }
        
        for (int i = 0; i < 10; i++)
        {
            threads[i] = new Thread(() =>
            {
                while (true)
                {
                    long number;
                    lock (lockObj)
                    {
                        if (primeQueue.Count == 0)
                            break;
                        number = primeQueue.Dequeue();
                    }

                    if (IsPrime(number))
                    {
                        lock (lockObj)
                        {
                            numbersProcessed++;
                            primeCount++;
                        }
                        Console.Write($"{number}, ");
                    }
                    else
                    {
                        lock (lockObj)
                        {
                            numbersProcessed++;
                        }
                    }
                }
            });
            threads[i].Start();
        }
        
        for (int i = 0; i < 10; i++)
        {
            threads[i].Join();
        }

        stopwatch.Stop();

        Console.WriteLine(); // New line after all primes are printed
        Console.WriteLine();

        // Should find 43427 primes for range_count = 1000000
        Console.WriteLine($"Numbers processed = {numbersProcessed}");
        Console.WriteLine($"Primes found      = {primeCount}");
        Console.WriteLine($"Total time        = {stopwatch.Elapsed}");        
    }
}