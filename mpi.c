// Libraries
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

// Struct for storing pixel data
typedef struct
{
    unsigned char b, g, r; // Blue, Green, Red
} pixel;
// Main function
int main(int argc, char *argv[])
{
    // MPI variables
    int myrank, nprocs;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;

    MPI_Init(&argc, &argv);                            // initializes the MPI environment
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);            // get the number of processes
    MPI_Comm_rank(MPI_COMM_WORLD, &myrank);            // get the rank of the process
    MPI_Get_processor_name(processor_name, &name_len); // get the name of the processor

    FILE *input_file, *output_file, *lecturas;
    input_file = fopen("f4.bmp", "rb"); // Original image
    float total_r = 0, total_g = 0, total_b = 0;

    int y, x, i, j;
    // Read BMP header
    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, input_file);

    // Extract image dimensions
    int width = *(int *)&header[18];
    int height = *(int *)&header[22];

    // Calculate image padding
    int padding = 0;
    while ((width * 3 + padding) % 4 != 0)
    {
        padding++;
    }

    // Allocate memory for image data
    pixel *image_data = (pixel *)malloc(width * height * sizeof(pixel));
    // Read image data
    fread(image_data, sizeof(pixel), width * height, input_file);
    int num_output_files = 2; // Number of output files

    // omp_set_num_threads(NUM_THREADS);
    // #pragma omp parallel for shared(image_data) private(output_file, y, x, i, j, total_b, total_r, total_g ) schedule(dynamic)
    if (myrank < nprocs)
    {                                           // If the process rank is less than the number of processes
        int n = nprocs - myrank;                // Number of files to process
        char filename[50];                      // Filename string
        sprintf(filename, "blurred_%d.bmp", n); // Create the filename
        output_file = fopen(filename, "wb");    // Open the output file

        // Blur image
        int kernel_size = 11 + n * 2; // value increases by 2 for each increment in n
        float kernel[kernel_size][kernel_size];
        float kernel_sum = 0; // Initialize kernel sum value
        for (int i = 0; i < kernel_size; i++)
        { // For each kernel row
            for (int j = 0; j < kernel_size; j++)
            {                                                            // For each kernel column
                kernel[i][j] = 1.0 / (float)(kernel_size * kernel_size); // Set kernel value
                kernel_sum += kernel[i][j];                              // Add the kernel value to the kernel sum
            }
        }

        // Write BMP header
        for (int i = 0; i < 54; i++)
        {                                  // For each byte in the header
            fputc(header[i], output_file); // Write the byte to the output file
        }

        for (int y = 0; y < height; y++)
        { // For each row
            for (int x = 0; x < width; x++)
            {                                          // For each column
                total_r = 0, total_g = 0, total_b = 0; // Reset the RGB values
                for (int i = 0; i < kernel_size; i++)
                { // For each kernel row
                    for (int j = 0; j < kernel_size; j++)
                    {                                       // For each kernel column
                        int nx = x - (kernel_size / 2) + j; // Kernel x index
                        int ny = y - (kernel_size / 2) + i; // Kernel y index
                        if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                        {                                                   // If the index is not out of bounds
                            int index = ny * width + nx;                    // Calculate the index of the pixel
                            float kernel_value = kernel[i][j] / kernel_sum; // Get the kernel value
                            // Sum the RGB values
                            total_r += kernel_value * image_data[index].r;
                            total_g += kernel_value * image_data[index].g;
                            total_b += kernel_value * image_data[index].b;
                        }
                    }
                }
                // Create the blurred pixel
                pixel blurred_pixel = {
                    (unsigned char)total_b,
                    (unsigned char)total_g,
                    (unsigned char)total_r};
                // Write the pixels to the output file
                fputc(blurred_pixel.b, output_file);
                fputc(blurred_pixel.g, output_file);
                fputc(blurred_pixel.r, output_file);
            }
            // Write the padding
            for (int i = 0; i < padding; i++)
            {
                fputc(0, output_file);
            }
            // Print progress every 100 rows
            if ((y + 1) % 100 == 0)
            {
                printf("Processed %d rows from processor %d with a total of %d processors and image=%d from pc %s\n", y + 1, myrank, nprocs, n, processor_name);
            }
        }
        fclose(output_file); // Close the output file
    }
    // Clean up
    free(image_data);   // Free the image data
    fclose(input_file); // Close the input file
    MPI_Finalize();     // Finalize the MPI environment
    return 0;
}