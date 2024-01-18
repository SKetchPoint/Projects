#include "myglu.h"
/* a minimalist GLU (based on the MESA 3D implementation) for getting access to the most commonly used GLU functions (Eike Anderson, 2022) */

/* internal only functions (start) */

/*
** Make m an identity matrix
*/
static void __gluMakeIdentityd(GLdouble m[16])
{
    m[0+4*0] = 1.0; m[0+4*1] = 0.0; m[0+4*2] = 0.0; m[0+4*3] = 0.0;
    m[1+4*0] = 0.0; m[1+4*1] = 1.0; m[1+4*2] = 0.0; m[1+4*3] = 0.0;
    m[2+4*0] = 0.0; m[2+4*1] = 0.0; m[2+4*2] = 1.0; m[2+4*3] = 0.0;
    m[3+4*0] = 0.0; m[3+4*1] = 0.0; m[3+4*2] = 0.0; m[3+4*3] = 1.0;
}
static void __gluMakeIdentityf(GLfloat m[16])
{
    m[0+4*0] = 1.0; m[0+4*1] = 0.0; m[0+4*2] = 0.0; m[0+4*3] = 0.0;
    m[1+4*0] = 0.0; m[1+4*1] = 1.0; m[1+4*2] = 0.0; m[1+4*3] = 0.0;
    m[2+4*0] = 0.0; m[2+4*1] = 0.0; m[2+4*2] = 1.0; m[2+4*3] = 0.0;
    m[3+4*0] = 0.0; m[3+4*1] = 0.0; m[3+4*2] = 0.0; m[3+4*3] = 1.0;
}
/*
** normalizing a vector
*/
static void normalize(float v[3])
{
    float r;

    r = (float)sqrt( v[0]*v[0] + v[1]*v[1] + v[2]*v[2] );
    if (r == 0.0f) return;

    v[0] /= r;
    v[1] /= r;
    v[2] /= r;
}
/*
** cross product
*/
static void cross(float v1[3], float v2[3], float result[3])
{
    result[0] = v1[1]*v2[2] - v1[2]*v2[1];
    result[1] = v1[2]*v2[0] - v1[0]*v2[2];
    result[2] = v1[0]*v2[1] - v1[1]*v2[0];
}

/* internal only functions (end) */

/* set up a 2D orthagonal viewport */
void gluOrtho2D(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top)
{
    glOrtho(left, right, bottom, top, -1.0, 1.0);
}

/* set up a perspective viewport */
void gluPerspective(GLdouble fovy, GLdouble aspect, GLdouble zNear, GLdouble zFar)
{
    GLdouble m[4][4];
    double cotangent, deltaZ;
    double radians = fovy / 2.0 * __glPi / 180.0;
	double sine = sin(radians);

    deltaZ = zFar - zNear;
    if ((deltaZ == 0.0) || (sine == 0.0) || (aspect == 0.0)) {
	return;
    }
    cotangent = cos(radians) / sine;

    __gluMakeIdentityd(&m[0][0]);
    m[0][0] = cotangent / aspect;
    m[1][1] = cotangent;
    m[2][2] = -(zFar + zNear) / deltaZ;
    m[2][3] = -1.0;
    m[3][2] = -2.0 * zNear * zFar / deltaZ;
    m[3][3] = 0.0;
    glMultMatrixd(&m[0][0]);
}

/* setting up your GL camera */
void gluLookAt(GLdouble eyex, GLdouble eyey, GLdouble eyez, GLdouble centerx,
	  GLdouble centery, GLdouble centerz, GLdouble upx, GLdouble upy,
	  GLdouble upz)
{
    float forward[3], side[3], up[3];
    GLfloat m[4][4];

    forward[0] = (float)(centerx - eyex);
    forward[1] = (float)(centery - eyey);
    forward[2] = (float)(centerz - eyez);

    up[0] = (float)upx;
    up[1] = (float)upy;
    up[2] = (float)upz;

    normalize(forward);

    /* Side = forward x up */
    cross(forward, up, side);
    normalize(side);

    /* Recompute up as: up = side x forward */
    cross(side, forward, up);

    __gluMakeIdentityf(&m[0][0]);
    m[0][0] = (GLfloat)side[0];
    m[1][0] = (GLfloat)side[1];
    m[2][0] = (GLfloat)side[2];

    m[0][1] = (GLfloat)up[0];
    m[1][1] = (GLfloat)up[1];
    m[2][1] = (GLfloat)up[2];

    m[0][2] = (GLfloat)-forward[0];
    m[1][2] = (GLfloat)-forward[1];
    m[2][2] = (GLfloat)-forward[2];

    glMultMatrixf(&m[0][0]);
    glTranslated(-eyex, -eyey, -eyez);
}
