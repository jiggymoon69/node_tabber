import bpy

extra_math = [[" M ADD", "Add (A) MATH"], [" M SUBTRACT", "Subtract (S) MATH"], [" M MULTIPLY", "Multiply (M) MATH"], [" M DIVIDE", "Divide (D) MATH"],
[" M MULTIPLY_ADD", "Multiply Add (MA) MATH"], [" M POWER", "Power (P) MATH"],  [" M LOGARITHM", "Logarithm (L) MATH"], [" M SQRT", "Square Root (SQ) MATH"],
[" M INVERSE_SQRT", "Inverse Square Root (ISQ) MATH"], [" M ABSOLUTE", "Absolute (A) MATH"], [" M EXPONENT", "Exponent (E) MATH"], [" M MINIMUM", "Minimum (M) MATH"],
[" M MAXIMUM", "Maximum (M) MATH"], [" M LESS_THAN", "Less Than (LT) MATH"], [" M GREATER_THAN", "Greater Than (GT) MATH"], [" M SIGN", "Sign (S) MATH"],
[" M COMPARE", "Compare (C) MATH"], [" M SMOOTH_MIN", "Smooth Minimum (SM) MATH"], [" M SMOOTH_MAX", "Smooth Maximum (SM) MATH"], [" M ROUND", "Round (R) MATH"],
[" M FLOOR", "Floor (F) MATH"], [" M CEIL", "Ceiling (C) MATH"], [" M TRUNC", "Truncate (T) MATH"], [" M FRACT", "Fraction (F) MATH"],
[" M MODULO", "Modulo (M) MATH"], [" M WRAP", "Wrap (W) MATH"], [" M SNAP", "Snap (S) MATH"], [" M PINGPONG", "Ping-Pong (PP) MATH"],
[" M SINE", "Sine (S) MATH"], [" M COSINE", "Cosine (C) MATH"], [" M TANGENT", "Tangent (T) MATH"], [" M ARCSINE", "ArcSine (AS) MATH"],
[" M ARCCOSINE", "Arccosine (AC) MATH"], [" M ARCTANGENT", "Arctangent (AT) MATH"], [" M ARCTAN2", "Arctan2 (AT) MATH"], [" M SINH", "Hyperbolic Sine (HS) MATH"],
[" M COSH", "Hyperbolic Cosine (HC) MATH"], [" M TANH", "Hyperbolic Tangent (HT) MATH"], [" M RADIANS", "To Radians (TR) MATH"], [" M DEGREES", "To Degrees (TD) MATH"],
]

extra_vector_math = [[" VM ADD", "Add (A) VEC MATH"], [" VM SUBTRACT", "Subtract (S) VEC MATH"], [" VM MULTIPLY", "Multiply (M) VEC MATH"], [" VM DIVIDE", "Divide (D) VEC MATH"],
[" VM CROSS_PRODUCT", "Cross Product (CP) VEC MATH"], [" VM PROJECT", "Project (P) VEC MATH"],  [" VM REFLECT", "Reflect (R) VEC MATH"], [" VM DOT_PRODUCT", "Dot Product (DP) VEC MATH"],
[" VM DISTANCE", "Distance (D) VEC MATH"], [" VM LENGTH", "Length (L) VEC MATH"],  [" VM SCALE", "Scale (S) VEC MATH"], [" VM NORMALIZE", "Normalize (N) VEC MATH"],
[" VM ABSOLUTE", "Absolute (A) VEC MATH"], [" VM MINIMUM", "Minimum (M) VEC MATH"],
[" VM MAXIMUM", "Maximum (M) VEC MATH"],
[" VM FLOOR", "Floor (F) VEC MATH"], [" VM CEIL", "Ceiling (C) VEC MATH"], [" VM FRACT", "Fraction (F) VEC MATH"],
[" VM MODULO", "Modulo (M) VEC MATH"], [" VM WRAP", "Wrap (W) VEC MATH"], [" VM SNAP", "Snap (S) VEC MATH"],
[" VM SINE", "Sine (S) VEC MATH"], [" VM COSINE", "Cosine (C) VEC MATH"], [" VM TANGENT", "Tangent (T) VEC MATH"],
]

extra_color = [[" C VALUE", "Value (V) COLOR"], [" C COLOR", "Color (C) COLOR"], [" C SATURATION", "Saturation (S) COLOR"], [" C HUE", "Hue (H) COLOR"],
[" C DIVIDE", "Divide (D) COLOR"], [" C SUBTRACT", "Subtract (S) COLOR"],  [" C DIFFERENCE", "Difference (D) COLOR"],
[" C LINEAR_LIGHT", "Linear Light (LL) COLOR"], [" C SOFT_LIGHT", "Soft Light (SL) COLOR"],  [" C OVERLAY", "Overlay (O) COLOR"],
[" C ADD", "Add (A) COLOR"], [" C DODGE", "Dodge (D) COLOR"], [" C SCREEN", "Screen (S) COLOR"], [" C LIGHTEN", "Lighten (L) COLOR"],
[" C BURN", "Burn (B) COLOR"], [" C MULTIPLY", "Multiply (M) COLOR"], [" C DARKEN", "Darken (D) COLOR"], [" C MIX", "Mix (M) COLOR"],
]

