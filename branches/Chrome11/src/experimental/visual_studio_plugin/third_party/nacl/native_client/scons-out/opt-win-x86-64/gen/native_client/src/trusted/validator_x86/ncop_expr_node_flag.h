/* \gen\native_client\src\trusted\validator_x86\ncop_expr_node_flag.h
 * THIS FILE IS AUTO_GENERATED DO NOT EDIT.
 *
 * This file was auto-generated by enum_gen.py
 * from file ncop_expr_node_flag.enum
 */

#ifndef _GEN_NATIVE_CLIENT_SRC_TRUSTED_VALIDATOR_X86_NCOP_EXPR_NODE_FLAG_H__
#define _GEN_NATIVE_CLIENT_SRC_TRUSTED_VALIDATOR_X86_NCOP_EXPR_NODE_FLAG_H__
typedef enum NaClExpFlag {
  ExprSet = 0,
  ExprUsed = 1,
  ExprAddress = 2,
  ExprDest = 3,
  ExprSize8 = 4,
  ExprSize16 = 5,
  ExprSize32 = 6,
  ExprSize64 = 7,
  ExprUnsignedHex = 8,
  ExprSignedHex = 9,
  ExprUnsignedInt = 10,
  ExprSignedInt = 11,
  ExprImplicit = 12,
  ExprJumpTarget = 13,
  NaClExpFlagEnumSize = 14, /* special size marker */
} NaClExpFlag;

/* Returns the name of an NaClExpFlag constant. */
extern const char* NaClExpFlagName(NaClExpFlag name);

#endif /* _GEN_NATIVE_CLIENT_SRC_TRUSTED_VALIDATOR_X86_NCOP_EXPR_NODE_FLAG_H__ */