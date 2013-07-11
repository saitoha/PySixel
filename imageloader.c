#include <Python.h>
#include <structmember.h>

#include <stdlib.h>
#include <stdint.h>
#include <memory.h>
#include <math.h>
#include "stb_image.c"

/*****************************************************************************
 *
 * Pixel object
 *
 *****************************************************************************/

typedef struct _stbex_pixel {
    union {
        struct {
            uint8_t r;
            uint8_t g;
            uint8_t b;
            uint8_t a;
        };
        uint32_t color_index;
    };
} stbex_pixel;

stbex_pixel
stbex_pixel_new(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
{
    stbex_pixel p;

    p.r = r;
    p.g = g;
    p.b = b; 
    p.a = a;

    return p;
}

int
stbex_pixel_compare_r(const stbex_pixel *lhs, const stbex_pixel *rhs)
{
    return lhs->b > rhs->b ? 1: -1;
}

int
stbex_pixel_compare_g(const stbex_pixel *lhs, const stbex_pixel *rhs)
{
    return lhs->g > rhs->g ? 1: -1;
}

int
stbex_pixel_compare_b(const stbex_pixel *lhs, const stbex_pixel *rhs)
{
    return lhs->b > rhs->b ? 1: -1;
}

void
stbex_pixel_sort_r(stbex_pixel * const pixels, size_t npixels)
{
    qsort(pixels, npixels, sizeof(stbex_pixel),
          (int (*)(const void *, const void *))stbex_pixel_compare_r);
}

void
stbex_pixel_sort_g(stbex_pixel * const pixels, size_t npixels)
{
    qsort(pixels, npixels, sizeof(stbex_pixel),
          (int (*)(const void *, const void *))stbex_pixel_compare_g);
}

void
stbex_pixel_sort_b(stbex_pixel * const pixels, size_t npixels)
{
    qsort(pixels, npixels, sizeof(stbex_pixel),
          (int (*)(const void *, const void *))stbex_pixel_compare_b);
}


/*****************************************************************************
 *
 * Median cut
 *
 *****************************************************************************/

/** cube */
struct stbex_cube;
typedef struct _stbex_cube {
    uint8_t min_r;
    uint8_t min_g;
    uint8_t min_b;
    uint8_t max_r;
    uint8_t max_g;
    uint8_t max_b;
    size_t npixels;
    stbex_pixel *pixels;
    struct stbex_cube *left;
    struct stbex_cube *right;
} stbex_cube;

struct stbex_cube *
stbex_cube_new(stbex_pixel *pixels, size_t npixels)
{
    stbex_cube *cube;
   
    cube = malloc(sizeof(stbex_cube));
    cube->pixels = malloc(sizeof(stbex_pixel *) * npixels);
    memcpy(cube->pixels, pixels, sizeof(stbex_pixel *) * npixels);
    cube->npixels = npixels;
    cube->left = NULL;
    cube->right = NULL;
    return (struct stbex_cube *)cube;
}

void
stbex_cube_free(stbex_cube *cube, stbex_pixel *pixels)
{
    free(cube);
}

void
stbex_cube_fit(stbex_cube *cube)
{
    int i;
    stbex_pixel *p;

    cube->max_r = 0;
    cube->min_r = 255;
    cube->max_g = 0;
    cube->min_g = 255;
    cube->max_b = 0;
    cube->min_b = 255;

    for (i = 0; i < cube->npixels; i++) {
        p = cube->pixels + i;
        if (p->r < cube->min_r) {
            cube->min_r = p->r;
        }
        if (p->g < cube->min_g) {
            cube->min_g = p->g;
        }
        if (p->b < cube->min_b) {
            cube->min_b = p->b;
        }
        if (p->r > cube->max_r) {
            cube->max_r = p->r;
        }
        if (p->g > cube->max_g) {
            cube->max_g = p->g;
        }
        if (p->b > cube->max_b) {
            cube->max_b = p->b;
        }
    }
}

int
stbex_cube_hatch(stbex_cube *cube, int threshold)
{
    int length_r;
    int length_g;
    int length_b;
    int min_cubesize = 36;
    int i;
    int divide_point;

    if (cube->left != NULL && cube->right != NULL) {
        return stbex_cube_hatch(cube->left, threshold)
             + stbex_cube_hatch(cube->right, threshold);
    }

    stbex_cube_fit(cube);

    length_r = (int)cube->max_r - (int)cube->min_r;
    length_g = (int)cube->max_g - (int)cube->min_g;
    length_b = (int)cube->max_b - (int)cube->min_b;

    if (cube->npixels <= 8) {
        return cube->npixels;
    }
           
    if (cube->npixels < threshold) {
        if (length_r < 100 && length_g < 100 && length_b < 100) {
            return 1;
        }
    }

    divide_point = cube->npixels / 2;

    if (length_r > length_g) {
        if (length_r > length_b) {
            if (length_r < min_cubesize) {
                return 1;
            }
            stbex_pixel_sort_r(cube->pixels, cube->npixels);

            for (i = divide_point; i < cube->npixels; i++) {
                if (cube->pixels[i].r != cube->pixels[divide_point - 1].r) {
                    break;
                }
            }
            divide_point = i;
        } else {
            if (length_b < min_cubesize) {
                return 1;
            }
            stbex_pixel_sort_b(cube->pixels, cube->npixels);

            for (i = divide_point; i < cube->npixels; i++) {
                if (cube->pixels[i].b != cube->pixels[divide_point - 1].b) {
                    break;
                }
            }
            divide_point = i;
        }
    } else if (length_g > length_b) {
        if (length_g < min_cubesize) {
            return 1;
        }
        stbex_pixel_sort_g(cube->pixels, cube->npixels);

        for (i = divide_point; i < cube->npixels; i++) {
            if (cube->pixels[i].g != cube->pixels[divide_point - 1].g) {
                break;
            }
        }
        divide_point = i;

    } else {
        if (length_b < min_cubesize) {
            return 1;
        }
        stbex_pixel_sort_b(cube->pixels, cube->npixels);

        for (i = divide_point; i < cube->npixels; i++) {
            if (cube->pixels[i].b != cube->pixels[divide_point - 1].b) {
                break;
            }
        }
        divide_point = i;

    }

    if (i == cube->npixels) {
        return 1;
    }

    if (cube->npixels == divide_point + 1) {
        return 1;
    }

    cube->left = stbex_cube_new(cube->pixels, divide_point);
    cube->right = stbex_cube_new(cube->pixels + divide_point + 1,
                           cube->npixels - divide_point - 1);

    return 2;
}

void
stbex_cube_get_sample(stbex_cube *cube, stbex_pixel *samples, stbex_pixel *results, int *nresults)
{
    if (cube->left) {
        stbex_cube_get_sample((stbex_cube *)cube->left, samples, results, nresults);
        stbex_cube_get_sample((stbex_cube *)cube->right, samples, results, nresults);
    } else {
    stbex_cube_fit(cube);
        *(results + (*nresults)++) = stbex_pixel_new(cube->min_r, cube->min_g, cube->min_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->max_r, cube->min_g, cube->min_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->min_r, cube->max_g, cube->min_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->min_r, cube->min_g, cube->max_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->max_r, cube->max_g, cube->min_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->min_r, cube->max_g, cube->max_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->max_r, cube->min_g, cube->max_b, 0); 
        *(results + (*nresults)++) = stbex_pixel_new(cube->max_r, cube->max_g, cube->max_b, 0); 
        printf("(%d, %d, %d) - (%d, %d, %d) => %ld\n",
                        cube->min_r,
                        cube->min_g,
                        cube->min_b,
                        cube->max_r,
                        cube->max_g,
                        cube->max_b,
                        cube->npixels);
    }
}

/*****************************************************************************
 *
 * Coulor reduction
 *
 *****************************************************************************/

void
pset(uint8_t *data, int index, int depth, stbex_pixel *value)
{
    memcpy(data + index * depth, value, depth);
}

stbex_pixel *
pget(unsigned char *data, int index, int depth)
{
    return (stbex_pixel *)(data + index * depth);
}

stbex_pixel *
zigzag_pget(unsigned char *data, int index, int width, int depth)
{
    int n = (int)floor(sqrt((index + 1) * 8) * 0.5 - 0.5);
    int x, y;

    if ((n & 0x1) == 0) {
        y = index - n * (n + 1) / 2;
        x = n - y;
    } else {
        x = index - n * (n + 1) / 2;
        y = n - x;
    }
    return (stbex_pixel *)(data + (y * width + x) * depth);
}

stbex_pixel *
get_sample(unsigned char *data, int width, int height, int depth, int count)
{
    int i;
    int n = width * height / count;
    stbex_pixel *result = malloc(sizeof(stbex_pixel) * count);

    for (i = 0; i < count; i++) {
        result[i] = *zigzag_pget(data, i * n, width, depth);
    }
    return result;
}

unsigned char *
make_palette(unsigned char *data, int x, int y, int n, int c)
{
    int i;
    unsigned char *palette;
    const size_t sample_count = 1024;
    stbex_pixel *sample;
    stbex_cube *cube;
    int nresult = 0;
    int ncount;
    int count = 0;

    palette = malloc(c * n);
    sample = get_sample(data, x, y, n, sample_count);
    cube = (stbex_cube *)stbex_cube_new(sample, sample_count);

    for (ncount = sample_count / 2; ncount > 8; ncount /= 2) {
        count += stbex_cube_hatch(cube, ncount);
        if (count > c / 16) {
            break;
        }
        printf("[%d]-\n", count);
    }
    printf("[%d]-\n", count);

    stbex_pixel results[sample_count];
    stbex_cube_get_sample(cube, sample, (stbex_pixel *)results, &nresult);

    printf("[%ld -> %d]\n", sample_count, count); fflush(0);

    for (i = 0; i < c; i++) {
        memcpy(palette + i * 3, results + i, 3); 
    }
    return palette;
}

void add_offset(unsigned char *data, int i, int n, int roffset, int goffset, int boffset) {
    int r = data[i * n + 0] + roffset;
    int g = data[i * n + 1] + goffset;
    int b = data[i * n + 2] + boffset;

    if (r < 0) {
        r = 0;
    }
    if (g < 0) {
        g = 0;
    }
    if (b < 0) {
        b = 0;
    }
    if (r > 255) {
        r = 255;
    }
    if (g > 255) {
        g = 255;
    }
    if (b > 255) {
        b = 255;
    }

    data[i * n + 0] = (unsigned char)r;
    data[i * n + 1] = (unsigned char)g;
    data[i * n + 2] = (unsigned char)b;
}


unsigned char *
apply_palette(unsigned char *data,
              int width, int height, int depth,
              unsigned char *palette, int c,
              int use_diffusion)
{
    int i;
    int j;
    int x, y;
    int r = 0, g = 0, b = 0;
    int rdiff, gdiff, bdiff;
    int roffset, goffset, boffset;
    int distant;
    int diff;
    int index;
    unsigned char *result;

    result = malloc(width * height);

    for (y = 0; y < height; ++y) {
        for (x = 0; x < width; ++x) {
            i = y * width + x;
            r = data[i * depth + 0];
            g = data[i * depth + 1];
            b = data[i * depth + 2];
            diff = 256 * 256 * 3;
            index = -1;
            j = 1;
            while (1) {
                rdiff = r - (int)palette[j * 3 + 0];
                gdiff = g - (int)palette[j * 3 + 1];
                bdiff = b - (int)palette[j * 3 + 2];
                distant = rdiff * rdiff + gdiff * gdiff + bdiff * bdiff;
                if (distant < diff) {
                    diff = distant;
                    index = j;
                }
                j++;
                if (j == c) {
                    break;
                }
            }
            if (index > 0) {
                result[i] = index;
                if (1) {
                    roffset = (int)data[i * depth + 0] - (int)palette[index * 3 + 0];
                    goffset = (int)data[i * depth + 1] - (int)palette[index * 3 + 1];
                    boffset = (int)data[i * depth + 2] - (int)palette[index * 3 + 2];
                    if (y < height - 1) {
                        add_offset(data, i + width, depth,
                                   roffset * 5 / 16,
                                   goffset * 5 / 16,
                                   boffset * 5 / 16);
                        if (x > 1) {
                            add_offset(data, i + width - 1, depth,
                                       roffset * 3 / 16,
                                       goffset * 3 / 16,
                                       boffset * 3 / 16);
                            roffset -= roffset * 3 / 16;
                            goffset -= goffset * 3 / 16;
                            boffset -= boffset * 3 / 16;
                        }
                        if (x < width - 1) {
                            add_offset(data, i + width + 1, depth,
                                       roffset * 1 / 16,
                                       goffset * 1 / 16,
                                       boffset * 1 / 16);
                        }
                    }
                    if (x < width - 1) {
                        roffset -= roffset * 5 / 16;
                        goffset -= goffset * 5 / 16;
                        boffset -= boffset * 5 / 16;
                        roffset -= roffset * 3 / 16;
                        goffset -= goffset * 3 / 16;
                        boffset -= boffset * 3 / 16;
                        roffset -= roffset * 1 / 16;
                        goffset -= goffset * 1 / 16;
                        boffset -= boffset * 1 / 16;
                        add_offset(data, i + 1, depth,
                                   roffset,
                                   goffset,
                                   boffset);
                    }
                }
            }
        }
    }
    return result;
}

/*****************************************************************************
 *
 * Image object
 *
 *****************************************************************************/

/** Image object */
typedef struct _Image {
    PyObject_HEAD
    PyObject *data;
    PyObject *palette;
    unsigned char *original;
    int width;
    int height;
    int depth;
    int expected_width;
    int expected_height;
    int expected_depth;
} Image;

/** allocator */
static PyObject *
Image_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Image *self = (Image *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    self->data = Py_None;
    self->palette = Py_None;
    self->original = NULL;
    self->width = 0;
    self->height = 0;
    self->depth = 0;
    self->expected_width = 0;
    self->expected_height = 0;
    self->expected_depth = 0;

    return (PyObject *)self;
}
 
/** deallocator */
static void
Image_dealloc(Image *self)
{
    Py_XDECREF(self->data);
    Py_XDECREF(self->palette);

    if (self->original) {
        stbi_image_free(self->original);
        self->original = NULL;
    }

    self->ob_type->tp_free((PyObject*)self);
}

/** initializer */
static int
Image_init(Image *self, PyObject *args, PyObject *kwds)
{
    PyObject *data = NULL;
    PyObject *palette = NULL;
    PyObject *tmp;
   
    static char *kwlist[] = {
        "data",
        "palette",
        "width",
        "height",
        "depth",
        NULL
    };
   
    int result = PyArg_ParseTupleAndKeywords(args, kwds, "|Siii", kwlist,
                                             &data,
                                             &palette,
                                             &self->width,
                                             &self->height,
                                             &self->depth);
  
    if (!result) {
        return -1;
    }
   
    if (data) {
        tmp = self->data;
        Py_DECREF(tmp);
        Py_INCREF(data);
        self->data = data;
    }
   
    if (palette) {
        tmp = self->palette;
        Py_DECREF(tmp);
        Py_INCREF(data);
        self->palette = data;
    }
   
    return 0;
}


static PyMemberDef Image_members[] = {
    { NULL } 
};

static PyObject *
Image_getdata(Image *self)
{
    Py_INCREF(self->data);
    return self->data;
}

static PyObject *
Image_getpalette(Image *self)
{
    Py_INCREF(self->palette);
    return self->palette;
}
 
static PyObject *
Image_convert(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyTypeObject *type = (PyTypeObject *)PyObject_Type(self);

    if (type == NULL) {
        return NULL;
    }

    Image *src = (Image *)self;
    Image *dest = (Image *)type->tp_alloc(type, 0);

    if (dest == NULL) {
        return NULL;
    }

    if (src->data != Py_None) {
        Py_INCREF(src->data);
        dest->data = src->data;
    }
    if (src->palette != Py_None) {
        Py_INCREF(src->palette);
        dest->palette = src->palette;
    }
    dest->width = src->width;
    dest->height = src->height;
    dest->depth = src->depth;
    dest->original = malloc(src->width * src->height * src->depth);
    memcpy(dest->original, src->original, src->width * src->height * src->depth);
    dest->expected_width = src->expected_width;
    dest->expected_height = src->expected_height;
    dest->expected_depth = src->expected_depth;

    return (PyObject *)dest;
}
 
static PyObject *
Image_resize(PyObject *self, PyObject *args)
{
    PyTypeObject *type = (PyTypeObject *)PyObject_Type(self);

    Image *src = (Image *)self;
    Image *dest;
    unsigned char *data;
    int width, height;
    int gx, gy;
    int rx, ry;
    const size_t colors = 256;
    unsigned char *palette;

    if (!PyArg_ParseTuple(args, "(ii)", &width, &height)) {
        return NULL;
    }

    dest = (Image *)type->tp_alloc(type, 0);
    if (dest == NULL) {
        return NULL;
    }

    dest->depth = src->depth;
    dest->original = malloc(width * height * src->depth);

    for (gy = 0; gy <= height; ++gy) {
        ry = (src->height - 1) * gy / height;
        for (gx = 0; gx <= width; ++gx) {
            rx = (src->width - 1) * gx / width;
            stbex_pixel *p = pget(src->original, src->width * ry + rx, src->depth);
            pset(dest->original, width * gy + gx, dest->depth, p);
        }
    }

    palette = make_palette(dest->original, width, height, src->depth, colors);
    data = apply_palette(dest->original, width, height, src->depth, palette, colors, 1);

    dest->data = PyByteArray_FromStringAndSize((char const *)data, width * height);
    dest->palette = PyByteArray_FromStringAndSize((char const *)palette, colors * 3);

    dest->width = width;
    dest->height = height;
    dest->expected_width = src->expected_width;
    dest->expected_height = src->expected_height;
    dest->expected_depth = src->expected_depth;

    return (PyObject *)dest;
}

static PyMethodDef Image_methods[] = {
    {"getdata", (PyCFunction)Image_getdata, METH_NOARGS, "return pixel data" },
    {"getpalette", (PyCFunction)Image_getpalette, METH_NOARGS, "return palette data" },
    {"convert", (PyCFunction)Image_convert, METH_KEYWORDS, "convert image data" },
    {"resize", Image_resize, METH_VARARGS, "resize image data" },
    { NULL }  /* Sentinel */
};

static PyObject *
Image_getsize(Image *self, void *closure)
{
    PyObject *width = PyInt_FromLong(self->width);
    PyObject *height = PyInt_FromLong(self->height);
    return PyTuple_Pack(2, width, height);
}

static PyGetSetDef Image_getseters[] = {
    { "size", (getter)Image_getsize, NULL, "size", NULL },
    { NULL }  /* Sentinel */
}; 

static PyTypeObject ImageType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "stbi.Image",                             /*tp_name*/
    sizeof(Image),                            /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)Image_dealloc,                /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash */
    0,                                        /*tp_call*/
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "STB Image class",                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Image_methods,                            /* tp_methods */
    Image_members,                            /* tp_members */
    Image_getseters,                          /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)Image_init,                     /* tp_init */
    0,                                        /* tp_alloc */
    Image_new,                                /* tp_new */
};
 
/*
*/
static PyObject *
open(PyObject *self, PyObject *args)
{
    int x, y, n;
    PyObject *file;
    PyObject *chunk;
    unsigned char *buffer;
    long length;
    char *filename;
    const char *tp_name;
    unsigned char *data;
    unsigned char *imagedata;
    unsigned char *palette;
    const size_t colors = 256;

    if (!PyArg_ParseTuple(args, "O", &file)) {
        return NULL;
    }

    tp_name = file->ob_type->tp_name;

    if (strcmp(tp_name, "str") == 0) {
        filename = PyString_AsString(file);
        data = stbi_load(filename, &x, &y, &n, STBI_default);
        if (data == NULL) {
            return NULL;
        }
    } else if (strcmp(tp_name, "cStringIO.StringI") == 0) {
        chunk = PyObject_CallMethod(file, "getvalue", NULL);
        if (chunk == NULL) {
            return NULL;
        }
        PyString_AsStringAndSize(chunk, (char **)&buffer, &length);
        data = stbi_load_from_memory(buffer, length,
                                     &x, &y, &n, STBI_default);
        if (data == NULL) {
            return NULL;
        }
    } else {
        return NULL;
    }

    palette = make_palette(data, x, y, n, colors);
    imagedata = apply_palette(data, x, y, n, palette, colors, 1);

    Image *pimage = (Image *)ImageType.tp_alloc(&ImageType, 0);
    if (pimage == NULL) {
        return NULL;
    }

    pimage->data = PyByteArray_FromStringAndSize((char const *)imagedata, x * y);
    pimage->palette = PyByteArray_FromStringAndSize((char const *)palette, colors * 3);
    pimage->original = data;
    if (pimage->data == NULL) {
        Py_DECREF(pimage);
        return NULL;
    }
    pimage->width = x;
    pimage->height = y;
    pimage->depth = n;
    pimage->expected_width = x;
    pimage->expected_height = y;
    pimage->expected_depth = n;

    free(palette);
    free(imagedata);

    return (PyObject *)pimage;
}

static char imageloader_doc[] = "An image loader which provides a subset of PIL interface.\n";

static PyMethodDef methods[] = {
    { "open", open, METH_VARARGS, "load image by filename\n" },
    { NULL, NULL, 0, NULL}
};

/** module entry point */
extern void initimageloader(void)
{
    PyObject *m = Py_InitModule3("imageloader", methods, imageloader_doc);
    if (PyType_Ready(&ImageType) < 0) {
        return;
    }
    PyModule_AddObject(m, "Image", (PyObject *)&ImageType);
    PyModule_AddObject(m, "ADAPTIVE", Py_BuildValue("i", 1));
}

// EOF
