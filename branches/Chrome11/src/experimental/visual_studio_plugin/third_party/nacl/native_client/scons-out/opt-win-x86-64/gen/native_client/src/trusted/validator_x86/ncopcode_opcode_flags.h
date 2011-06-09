/* \gen\native_client\src\trusted\validator_x86\ncopcode_opcode_flags.h
 * THIS FILE IS AUTO_GENERATED DO NOT EDIT.
 *
 * This file was auto-generated by enum_gen.py
 * from file ncopcode_opcode_flags.enum
 */

#ifndef _GEN_NATIVE_CLIENT_SRC_TRUSTED_VALIDATOR_X86_NCOPCODE_OPCODE_FLAGS_H__
#define _GEN_NATIVE_CLIENT_SRC_TRUSTED_VALIDATOR_X86_NCOPCODE_OPCODE_FLAGS_H__
typedef enum NaClIFlag {
  OpcodeUsesRexW = 0,
  OpcodeHasRexR = 1,
  OpcodeInModRm = 2,
  OpcodeLtC0InModRm = 3,
  ModRmModIs0x3 = 4,
  OpcodeUsesModRm = 5,
  OpcodeHasImmed = 6,
  OpcodeHasImmed_b = 7,
  OpcodeHasImmed_w = 8,
  OpcodeHasImmed_v = 9,
  OpcodeHasImmed_p = 10,
  OpcodeHasImmed_o = 11,
  OpcodeHasImmed2_b = 12,
  OpcodeHasImmed2_w = 13,
  OpcodeHasImmed2_v = 14,
  OpcodeHasImmed_Addr = 15,
  OpcodePlusR = 16,
  OpcodePlusI = 17,
  OpcodeRex = 18,
  OpcodeLegacy = 19,
  OpcodeLockable = 20,
  Opcode32Only = 21,
  Opcode64Only = 22,
  OperandSize_b = 23,
  OperandSize_w = 24,
  OperandSize_v = 25,
  OperandSize_o = 26,
  AddressSize_w = 27,
  AddressSize_v = 28,
  AddressSize_o = 29,
  NaClIllegal = 30,
  OperandSizeDefaultIs64 = 31,
  OperandSizeForce64 = 32,
  AddressSizeDefaultIs32 = 33,
  IgnorePrefixDATA16 = 34,
  IgnorePrefixSEGCS = 35,
  NaClIFlagEnumSize = 36, /* special size marker */
} NaClIFlag;

/* Returns the name of an NaClIFlag constant. */
extern const char* NaClIFlagName(NaClIFlag name);

#endif /* _GEN_NATIVE_CLIENT_SRC_TRUSTED_VALIDATOR_X86_NCOPCODE_OPCODE_FLAGS_H__ */