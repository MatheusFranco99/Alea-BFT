# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messages.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emessages.proto\x12\npython_app\":\n\x08VCBCSend\x12\x0c\n\x04\x64\x61ta\x18\x01 \x02(\t\x12\x10\n\x08priority\x18\x02 \x02(\x05\x12\x0e\n\x06\x61uthor\x18\x03 \x02(\x05\"=\n\tVCBCReady\x12\x10\n\x08priority\x18\x01 \x02(\x05\x12\x0e\n\x06\x61uthor\x18\x02 \x02(\x05\x12\x0e\n\x06sender\x18\x03 \x02(\x05\"=\n\tVCBCFinal\x12\x10\n\x08priority\x18\x01 \x02(\x05\x12\x0e\n\x06\x61uthor\x18\x02 \x02(\x05\x12\x0e\n\x06sender\x18\x03 \x02(\x05\"X\n\x07\x41\x42\x41Init\x12\x0e\n\x06\x61uthor\x18\x01 \x02(\x05\x12\x10\n\x08priority\x18\x02 \x02(\x05\x12\r\n\x05round\x18\x03 \x02(\x05\x12\x0c\n\x04vote\x18\x04 \x02(\x05\x12\x0e\n\x06sender\x18\x05 \x02(\x05\"W\n\x06\x41\x42\x41\x41ux\x12\x0e\n\x06\x61uthor\x18\x01 \x02(\x05\x12\x10\n\x08priority\x18\x02 \x02(\x05\x12\r\n\x05round\x18\x03 \x02(\x05\x12\x0c\n\x04vote\x18\x04 \x02(\x05\x12\x0e\n\x06sender\x18\x05 \x02(\x05\"Y\n\x07\x41\x42\x41\x43onf\x12\x0e\n\x06\x61uthor\x18\x01 \x02(\x05\x12\x10\n\x08priority\x18\x02 \x02(\x05\x12\r\n\x05round\x18\x03 \x02(\x05\x12\r\n\x05votes\x18\x04 \x03(\x05\x12\x0e\n\x06sender\x18\x05 \x02(\x05\"K\n\tABAFinish\x12\x0e\n\x06\x61uthor\x18\x01 \x02(\x05\x12\x10\n\x08priority\x18\x02 \x02(\x05\x12\x0c\n\x04vote\x18\x03 \x02(\x05\x12\x0e\n\x06sender\x18\x04 \x02(\x05')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'messages_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _VCBCSEND._serialized_start=30
  _VCBCSEND._serialized_end=88
  _VCBCREADY._serialized_start=90
  _VCBCREADY._serialized_end=151
  _VCBCFINAL._serialized_start=153
  _VCBCFINAL._serialized_end=214
  _ABAINIT._serialized_start=216
  _ABAINIT._serialized_end=304
  _ABAAUX._serialized_start=306
  _ABAAUX._serialized_end=393
  _ABACONF._serialized_start=395
  _ABACONF._serialized_end=484
  _ABAFINISH._serialized_start=486
  _ABAFINISH._serialized_end=561
# @@protoc_insertion_point(module_scope)
