#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <libusb-1.0/libusb.h>

#define VENDOR  0x05ac
#define PRODUCT 0x1227

static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1.0e6;
}

int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

int main(void) {
    libusb_context *ctx = NULL;
    if (libusb_init(&ctx) < 0) { fprintf(stderr, "libusb_init fallo\n"); return 1; }

    libusb_device **list = NULL;
    ssize_t n = libusb_get_device_list(ctx, &list);
    if (n < 0) { fprintf(stderr, "get_device_list fallo\n"); return 1; }

    libusb_device *dev = NULL;
    for (ssize_t i = 0; i < n; i++) {
        struct libusb_device_descriptor d;
        if (libusb_get_device_descriptor(list[i], &d) != 0) continue;
        if (d.idVendor == VENDOR && d.idProduct == PRODUCT) { dev = list[i]; break; }
    }
    if (!dev) { fprintf(stderr, "dispositivo 05ac:1227 NO encontrado\n"); return 1; }

    libusb_device_handle *h = NULL;
    int r = libusb_open(dev, &h);
    if (r < 0) { fprintf(stderr, "libusb_open fallo: %s\n", libusb_strerror(r)); return 1; }

    if (libusb_kernel_driver_active(h, 0) == 1) libusb_detach_kernel_driver(h, 0);
    r = libusb_claim_interface(h, 0);
    if (r < 0) { fprintf(stderr, "claim_interface fallo: %s\n", libusb_strerror(r)); return 1; }

    unsigned char buf[64];
    int N = 300;
    double *t = malloc(sizeof(double) * N);
    int ok = 0;

    /* DFU_GETSTATUS (bRequest=3), wLength=6 es la longitud real del status */
    for (int i = 0; i < N; i++) {
        double a = now_ms();
        int rr = libusb_control_transfer(h,
            LIBUSB_ENDPOINT_IN | LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
            0x03, 0x0000, 0x0000, buf, 6, 1000);
        double b = now_ms();
        if (rr == 6) { t[ok++] = b - a; }
    }

    if (ok == 0) { fprintf(stderr, "0 transferencias exitosas\n"); return 1; }

    double sum = 0;
    for (int i = 0; i < ok; i++) sum += t[i];
    qsort(t, ok, sizeof(double), cmp_d);
    double mean = sum / ok;
    double p50 = t[ok / 2];
    double p95 = t[(int)(ok * 0.95)];
    double p99 = t[(int)(ok * 0.99)];
    double mx  = t[ok - 1];

    printf("=== LATENCIA DE TRANSFERENCIAS DE CONTROL USB (DFU GET_STATUS) ===\n");
    printf("muestras exitosas : %d / %d\n", ok, N);
    printf("media             : %.3f ms\n", mean);
    printf("p50 (mediana)     : %.3f ms\n", p50);
    printf("p95               : %.3f ms\n", p95);
    printf("p99               : %.3f ms\n", p99);
    printf("maximo            : %.3f ms\n\n", mx);
    printf("checkm8 necesita precision de ~0.1-1 ms con microsegundos de jitter.\n");
    if (p50 < 1.0 && (mx - p50) < 1.0)
        printf("VEREDICTO: latencia BAJA -> el timing del exploit es VIABLE\n");
    else if (p50 < 5.0)
        printf("VEREDICTO: latencia MEDIA-MODERADA ->Podria funcionar con reintentos\n");
    else
        printf("VEREDICTO: latencia ALTA -> el timing del exploit es inviable\n");

    libusb_release_interface(h, 0);
    libusb_close(h);
    libusb_free_device_list(list, 1);
    libusb_exit(ctx);
    return 0;
}
