#ifndef _MY_GLU_
#define _MY_GLU_

#include <math.h>
#include <GL/gl.h>

/* a minimalist GLU (based on the MESA 3D implementation) for getting access to the most commonly used GLU functions (Eike Anderson, 2022) */
#define __glPi 3.14159265358979323846

void gluOrtho2D(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top); /* set up a 2D orthagonal viewport */

void gluPerspective(GLdouble fovy, GLdouble aspect, GLdouble zNear, GLdouble zFar); /* set up a perspective viewport */

void gluLookAt(GLdouble eyex, GLdouble eyey, GLdouble eyez, GLdouble centerx,
	  GLdouble centery, GLdouble centerz, GLdouble upx, GLdouble upy,
	  GLdouble upz); /* setting up your GL camera */

#endif
