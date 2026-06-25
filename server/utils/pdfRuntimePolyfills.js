/* eslint-disable */

/**
 * @function normalizeMatrixInit
 * @description Normalizes DOMMatrix constructor inputs into a six-value 2D transform tuple.
 * @collaboration PDF runtime polyfill, backend document service boot stability, pdf-parse compatibility.
 */
function normalizeMatrixInit(init) {
  if (!init) {
    return [1, 0, 0, 1, 0, 0];
  }

  if (Array.isArray(init) || ArrayBuffer.isView(init)) {
    const values = Array.from(init).map((value) => Number(value || 0));

    if (values.length === 6) {
      return values;
    }

    if (values.length >= 16) {
      return [values[0], values[1], values[4], values[5], values[12], values[13]];
    }
  }

  if (typeof init === 'object') {
    return [
      Number(init.a ?? init.m11 ?? 1),
      Number(init.b ?? init.m12 ?? 0),
      Number(init.c ?? init.m21 ?? 0),
      Number(init.d ?? init.m22 ?? 1),
      Number(init.e ?? init.m41 ?? 0),
      Number(init.f ?? init.m42 ?? 0),
    ];
  }

  return [1, 0, 0, 1, 0, 0];
}

/**
 * @function multiply2d
 * @description Multiplies two six-value 2D matrix tuples.
 * @collaboration PDF runtime polyfill, DOMMatrix compatibility, server-side PDF parsing.
 */
function multiply2d(left, right) {
  return [
    left[0] * right[0] + left[2] * right[1],
    left[1] * right[0] + left[3] * right[1],
    left[0] * right[2] + left[2] * right[3],
    left[1] * right[2] + left[3] * right[3],
    left[0] * right[4] + left[2] * right[5] + left[4],
    left[1] * right[4] + left[3] * right[5] + left[5],
  ];
}

/**
 * @function radians
 * @description Converts degrees into radians for DOMMatrix rotation helpers.
 * @collaboration PDF runtime polyfill, geometry transform compatibility, backend boot stability.
 */
function radians(degrees) {
  return (Number(degrees || 0) * Math.PI) / 180;
}

/**
 * @function createRotationMatrix
 * @description Builds a six-value rotation matrix tuple.
 * @collaboration PDF runtime polyfill, DOMMatrix rotation support, pdf-parse compatibility.
 */
function createRotationMatrix(angle) {
  const value = radians(angle);
  const cos = Math.cos(value);
  const sin = Math.sin(value);

  return [cos, sin, -sin, cos, 0, 0];
}

/**
 * @function createScaleMatrix
 * @description Builds a six-value scale matrix tuple.
 * @collaboration PDF runtime polyfill, DOMMatrix scale support, server-side document processing.
 */
function createScaleMatrix(scaleX, scaleY) {
  const x = Number(scaleX ?? 1);
  const y = Number(scaleY ?? x);

  return [x, 0, 0, y, 0, 0];
}

/**
 * @function createTranslationMatrix
 * @description Builds a six-value translation matrix tuple.
 * @collaboration PDF runtime polyfill, DOMMatrix translate support, backend document parsing.
 */
function createTranslationMatrix(x, y) {
  return [1, 0, 0, 1, Number(x || 0), Number(y || 0)];
}

/**
 * @function WilsyPdfDOMPoint
 * @description Provides a minimal DOMPoint implementation for Node PDF parsing.
 * @collaboration PDF runtime polyfill, backend document service boot stability, pdf-parse compatibility.
 */
class WilsyPdfDOMPoint {
  x = 0;
  y = 0;
  z = 0;
  w = 1;

  constructor(x = 0, y = 0, z = 0, w = 1) {
    this.x = Number(x || 0);
    this.y = Number(y || 0);
    this.z = Number(z || 0);
    this.w = Number(w || 1);
  }

  matrixTransform(matrix) {
    const domMatrix = matrix instanceof WilsyPdfDOMMatrix ? matrix : new WilsyPdfDOMMatrix(matrix);

    return new WilsyPdfDOMPoint(
      this.x * domMatrix.a + this.y * domMatrix.c + domMatrix.e,
      this.x * domMatrix.b + this.y * domMatrix.d + domMatrix.f,
      this.z,
      this.w
    );
  }

  toJSON() {
    return {
      x: this.x,
      y: this.y,
      z: this.z,
      w: this.w,
    };
  }
}

/**
 * @function WilsyPdfDOMMatrix
 * @description Provides a minimal DOMMatrix implementation for Node PDF parsing.
 * @collaboration PDF runtime polyfill, backend document service boot stability, pdf-parse compatibility.
 */
class WilsyPdfDOMMatrix {
  constructor(init) {
    this.setFromTuple(normalizeMatrixInit(init));
  }

  get is2D() {
    return true;
  }

  get isIdentity() {
    return (
      this.a === 1 && this.b === 0 && this.c === 0 && this.d === 1 && this.e === 0 && this.f === 0
    );
  }

  setFromTuple(tuple) {
    [this.a, this.b, this.c, this.d, this.e, this.f] = tuple;

    this.m11 = this.a;
    this.m12 = this.b;
    this.m13 = 0;
    this.m14 = 0;
    this.m21 = this.c;
    this.m22 = this.d;
    this.m23 = 0;
    this.m24 = 0;
    this.m31 = 0;
    this.m32 = 0;
    this.m33 = 1;
    this.m34 = 0;
    this.m41 = this.e;
    this.m42 = this.f;
    this.m43 = 0;
    this.m44 = 1;

    return this;
  }

  toTuple() {
    return [this.a, this.b, this.c, this.d, this.e, this.f];
  }

  multiply(other) {
    return new WilsyPdfDOMMatrix(multiply2d(this.toTuple(), normalizeMatrixInit(other)));
  }

  multiplySelf(other) {
    return this.setFromTuple(multiply2d(this.toTuple(), normalizeMatrixInit(other)));
  }

  preMultiplySelf(other) {
    return this.setFromTuple(multiply2d(normalizeMatrixInit(other), this.toTuple()));
  }

  translate(tx = 0, ty = 0) {
    return new WilsyPdfDOMMatrix(this.toTuple()).translateSelf(tx, ty);
  }

  translateSelf(tx = 0, ty = 0) {
    return this.multiplySelf(createTranslationMatrix(tx, ty));
  }

  scale(scaleX = 1, scaleY = scaleX) {
    return new WilsyPdfDOMMatrix(this.toTuple()).scaleSelf(scaleX, scaleY);
  }

  scaleSelf(scaleX = 1, scaleY = scaleX) {
    return this.multiplySelf(createScaleMatrix(scaleX, scaleY));
  }

  rotate(angle = 0) {
    return new WilsyPdfDOMMatrix(this.toTuple()).rotateSelf(angle);
  }

  rotateSelf(angle = 0) {
    return this.multiplySelf(createRotationMatrix(angle));
  }

  transformPoint(point = {}) {
    return new WilsyPdfDOMPoint(
      point.x || 0,
      point.y || 0,
      point.z || 0,
      point.w || 1
    ).matrixTransform(this);
  }

  inverse() {
    return new WilsyPdfDOMMatrix(this.toTuple()).invertSelf();
  }

  invertSelf() {
    const determinant = this.a * this.d - this.b * this.c;

    if (!determinant) {
      return this.setFromTuple([
        Number.NaN,
        Number.NaN,
        Number.NaN,
        Number.NaN,
        Number.NaN,
        Number.NaN,
      ]);
    }

    return this.setFromTuple([
      this.d / determinant,
      -this.b / determinant,
      -this.c / determinant,
      this.a / determinant,
      (this.c * this.f - this.d * this.e) / determinant,
      (this.b * this.e - this.a * this.f) / determinant,
    ]);
  }

  toFloat32Array() {
    return new Float32Array(this.toFloat64Array());
  }

  toFloat64Array() {
    return new Float64Array([
      this.m11,
      this.m12,
      this.m13,
      this.m14,
      this.m21,
      this.m22,
      this.m23,
      this.m24,
      this.m31,
      this.m32,
      this.m33,
      this.m34,
      this.m41,
      this.m42,
      this.m43,
      this.m44,
    ]);
  }

  toJSON() {
    return {
      a: this.a,
      b: this.b,
      c: this.c,
      d: this.d,
      e: this.e,
      f: this.f,
      is2D: this.is2D,
      isIdentity: this.isIdentity,
    };
  }

  toString() {
    return `matrix(${this.a}, ${this.b}, ${this.c}, ${this.d}, ${this.e}, ${this.f})`;
  }
}

/**
 * @function WilsyPdfImageData
 * @description Provides a minimal ImageData implementation for Node PDF parsing.
 * @collaboration PDF runtime polyfill, backend document service boot stability, pdf-parse compatibility.
 */
class WilsyPdfImageData {
  constructor(data, width, height) {
    this.data = data || new Uint8ClampedArray(Number(width || 0) * Number(height || 0) * 4);
    this.width = Number(width || 0);
    this.height = Number(height || 0);
    this.colorSpace = 'srgb';
  }
}

/**
 * @function WilsyPdfPath2D
 * @description Provides a minimal Path2D implementation for Node PDF parsing.
 * @collaboration PDF runtime polyfill, backend document service boot stability, pdf-parse compatibility.
 */
class WilsyPdfPath2D {
  constructor(path) {
    this.path = path || '';
  }

  addPath() {}

  closePath() {}

  moveTo() {}

  lineTo() {}

  bezierCurveTo() {}

  quadraticCurveTo() {}

  rect() {}

  arc() {}

  ellipse() {}
}

/**
 * @function installPdfRuntimePolyfills
 * @description Installs minimal server-side browser geometry globals required by pdf-parse/pdfjs under Node.
 * @collaboration Backend boot stability, documentService isolation, PDF parsing compatibility.
 */
export function installPdfRuntimePolyfills() {
  if (typeof globalThis.DOMMatrix === 'undefined') {
    globalThis.DOMMatrix = WilsyPdfDOMMatrix;
  }

  if (typeof globalThis.DOMPoint === 'undefined') {
    globalThis.DOMPoint = WilsyPdfDOMPoint;
  }

  if (typeof globalThis.DOMPointReadOnly === 'undefined') {
    globalThis.DOMPointReadOnly = WilsyPdfDOMPoint;
  }

  if (typeof globalThis.DOMMatrixReadOnly === 'undefined') {
    globalThis.DOMMatrixReadOnly = WilsyPdfDOMMatrix;
  }

  if (typeof globalThis.ImageData === 'undefined') {
    globalThis.ImageData = WilsyPdfImageData;
  }

  if (typeof globalThis.Path2D === 'undefined') {
    globalThis.Path2D = WilsyPdfPath2D;
  }

  return {
    domMatrix: typeof globalThis.DOMMatrix !== 'undefined',
    domPoint: typeof globalThis.DOMPoint !== 'undefined',
    imageData: typeof globalThis.ImageData !== 'undefined',
    path2D: typeof globalThis.Path2D !== 'undefined',
  };
}
