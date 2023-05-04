#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <string.h>

typedef struct
{ // Total: 3 bytes
    unsigned char b, g, r;
} pixel;

int main(int argc, char *argv[])
{
    // MPI variables
    int myrank, nprocs;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myrank);
    MPI_Get_processor_name(processor_name, &name_len);

    FILE *input_file, *output_file, *lecturas;

    input_file = fopen(argv[1], "rb"); // Imagen original a transformar
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
    {
        int n = nprocs - myrank;
        char filename[50];
        sprintf(filename, "./nueva_blur/blurred_%d.bmp", n);
        output_file = fopen(filename, "wb");

        // Blur image
        int kernel_size = 11 + n * 2;
        float kernel[kernel_size][kernel_size];
        float kernel_sum = 0;
        for (int i = 0; i < kernel_size; i++)
        {
            for (int j = 0; j < kernel_size; j++)
            {
                kernel[i][j] = 1.0 / (float)(kernel_size * kernel_size);
                kernel_sum += kernel[i][j];
            }
        }

        // Write BMP header
        for (int i = 0; i < 54; i++)
        {
            fputc(header[i], output_file);
        }

        for (int y = 0; y < height; y++)
        { // For each row
            for (int x = 0; x < width; x++)
            {                                          // For each column
                total_r = 0, total_g = 0, total_b = 0; // Reset color values
                for (int i = 0; i < kernel_size; i++)
                { // For each kernel row
                    for (int j = 0; j < kernel_size; j++)
                    {                                       // For each kernel column
                        int nx = x - (kernel_size / 2) + j; // Kernel x index
                        int ny = y - (kernel_size / 2) + i; // Kernel y index
                        if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                        {                                                   // If index is not out of bounds
                            int index = ny * width + nx;                    // Calculate kernel index
                            float kernel_value = kernel[i][j] / kernel_sum; //  Normalize kernel value
                            total_r += kernel_value * image_data[index].r;  // Sum reds
                            total_g += kernel_value * image_data[index].g;  // Sum greens
                            total_b += kernel_value * image_data[index].b;  // Sum blues
                        }
                    }
                }
                // Create blurred pixel
                pixel blurred_pixel = {
                    (unsigned char)total_b,
                    (unsigned char)total_g,
                    (unsigned char)total_r};
                // Write blurred pixel to output file
                fputc(blurred_pixel.b, output_file);
                fputc(blurred_pixel.g, output_file);
                fputc(blurred_pixel.r, output_file);
            }
            // Write image padding
            for (int i = 0; i < padding; i++)
            {
                fputc(0, output_file);
            }
            // Print progress
            if ((y + 1) % 100 == 0)
            {
                printf("Processed %d rows from processor %d with a total of %d processors and image=%d from pc %s\n", y + 1, myrank, nprocs, n, processor_name);
            }
        }
        // Close output file
        fclose(output_file);
    }
    // Clean up
    free(image_data);
    fclose(input_file);
    MPI_Finalize();
    return 0;
}