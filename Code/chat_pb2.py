# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: chat.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'chat.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\"(\n\x14\x43heckUsernameRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"5\n\x15\x43heckUsernameResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\":\n\x14\x43heckPasswordRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"5\n\x15\x43heckPasswordResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"7\n\x11\x43reateUserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"2\n\x12\x43reateUserResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"\'\n\x13\x43onfirmLoginRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"e\n\x14\x43onfirmLoginResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\x12\x17\n\x0fnum_unread_msgs\x18\x02 \x01(\x03\x12\x16\n\x0enum_total_msgs\x18\x03 \x01(\x03\"(\n\x14\x43onfirmLogoutRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"5\n\x15\x43onfirmLogoutResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"\x17\n\x15GetOnlineUsersRequest\"E\n\x16GetOnlineUsersResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\x12\r\n\x05users\x18\x02 \x03(\t\" \n\x0fGetUsersRequest\x12\r\n\x05query\x18\x01 \x01(\t\"?\n\x10GetUsersResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\x12\r\n\x05users\x18\x02 \x03(\t\"~\n\rMessageObject\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0e\n\x06sender\x18\x02 \x01(\t\x12\x11\n\trecipient\x18\x03 \x01(\t\x12\x11\n\ttime_sent\x18\x04 \x01(\t\x12\x0c\n\x04read\x18\x05 \x01(\x08\x12\x0f\n\x07subject\x18\x06 \x01(\t\x12\x0c\n\x04\x62ody\x18\x07 \x01(\t\":\n\x12SendMessageRequest\x12$\n\x07message\x18\x01 \x01(\x0b\x32\x13.chat.MessageObject\"3\n\x13SendMessageResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"Y\n\x11GetMessageRequest\x12\x0e\n\x06offset\x18\x01 \x01(\x03\x12\r\n\x05limit\x18\x02 \x01(\x03\x12\x13\n\x0bunread_only\x18\x03 \x01(\x08\x12\x10\n\x08username\x18\x04 \x01(\t\"Y\n\x12GetMessageResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\x12%\n\x08messages\x18\x02 \x03(\x0b\x32\x13.chat.MessageObject\":\n\x12\x43onfirmReadRequest\x12\x12\n\nmessage_id\x18\x01 \x01(\x03\x12\x10\n\x08username\x18\x02 \x01(\t\"3\n\x13\x43onfirmReadResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"*\n\x14\x44\x65leteMessageRequest\x12\x12\n\nmessage_id\x18\x01 \x03(\x03\"5\n\x15\x44\x65leteMessageResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"%\n\x11\x44\x65leteUserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"2\n\x12\x44\x65leteUserResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\"\x15\n\x13GetDatabasesRequest\"i\n\x14GetDatabasesResponse\x12\x1c\n\x06status\x18\x01 \x01(\x0e\x32\x0c.chat.Status\x12\x19\n\x11password_database\x18\x02 \x01(\x0c\x12\x18\n\x10message_database\x18\x03 \x01(\x0c*F\n\x06Status\x12\x0b\n\x07PENDING\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\x12\t\n\x05MATCH\x10\x02\x12\x0c\n\x08NO_MATCH\x10\x03\x12\t\n\x05\x45RROR\x10\x04\x32\x96\x07\n\x0b\x43hatService\x12H\n\rCheckUsername\x12\x1a.chat.CheckUsernameRequest\x1a\x1b.chat.CheckUsernameResponse\x12H\n\rCheckPassword\x12\x1a.chat.CheckPasswordRequest\x1a\x1b.chat.CheckPasswordResponse\x12?\n\nCreateUser\x12\x17.chat.CreateUserRequest\x1a\x18.chat.CreateUserResponse\x12\x45\n\x0c\x43onfirmLogin\x12\x19.chat.ConfirmLoginRequest\x1a\x1a.chat.ConfirmLoginResponse\x12H\n\rConfirmLogout\x12\x1a.chat.ConfirmLogoutRequest\x1a\x1b.chat.ConfirmLogoutResponse\x12K\n\x0eGetOnlineUsers\x12\x1b.chat.GetOnlineUsersRequest\x1a\x1c.chat.GetOnlineUsersResponse\x12\x39\n\x08GetUsers\x12\x15.chat.GetUsersRequest\x1a\x16.chat.GetUsersResponse\x12\x42\n\x0bSendMessage\x12\x18.chat.SendMessageRequest\x1a\x19.chat.SendMessageResponse\x12?\n\nGetMessage\x12\x17.chat.GetMessageRequest\x1a\x18.chat.GetMessageResponse\x12\x42\n\x0b\x43onfirmRead\x12\x18.chat.ConfirmReadRequest\x1a\x19.chat.ConfirmReadResponse\x12H\n\rDeleteMessage\x12\x1a.chat.DeleteMessageRequest\x1a\x1b.chat.DeleteMessageResponse\x12?\n\nDeleteUser\x12\x17.chat.DeleteUserRequest\x1a\x18.chat.DeleteUserResponse\x12\x45\n\x0cGetDatabases\x12\x19.chat.GetDatabasesRequest\x1a\x1a.chat.GetDatabasesResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STATUS']._serialized_start=1633
  _globals['_STATUS']._serialized_end=1703
  _globals['_CHECKUSERNAMEREQUEST']._serialized_start=20
  _globals['_CHECKUSERNAMEREQUEST']._serialized_end=60
  _globals['_CHECKUSERNAMERESPONSE']._serialized_start=62
  _globals['_CHECKUSERNAMERESPONSE']._serialized_end=115
  _globals['_CHECKPASSWORDREQUEST']._serialized_start=117
  _globals['_CHECKPASSWORDREQUEST']._serialized_end=175
  _globals['_CHECKPASSWORDRESPONSE']._serialized_start=177
  _globals['_CHECKPASSWORDRESPONSE']._serialized_end=230
  _globals['_CREATEUSERREQUEST']._serialized_start=232
  _globals['_CREATEUSERREQUEST']._serialized_end=287
  _globals['_CREATEUSERRESPONSE']._serialized_start=289
  _globals['_CREATEUSERRESPONSE']._serialized_end=339
  _globals['_CONFIRMLOGINREQUEST']._serialized_start=341
  _globals['_CONFIRMLOGINREQUEST']._serialized_end=380
  _globals['_CONFIRMLOGINRESPONSE']._serialized_start=382
  _globals['_CONFIRMLOGINRESPONSE']._serialized_end=483
  _globals['_CONFIRMLOGOUTREQUEST']._serialized_start=485
  _globals['_CONFIRMLOGOUTREQUEST']._serialized_end=525
  _globals['_CONFIRMLOGOUTRESPONSE']._serialized_start=527
  _globals['_CONFIRMLOGOUTRESPONSE']._serialized_end=580
  _globals['_GETONLINEUSERSREQUEST']._serialized_start=582
  _globals['_GETONLINEUSERSREQUEST']._serialized_end=605
  _globals['_GETONLINEUSERSRESPONSE']._serialized_start=607
  _globals['_GETONLINEUSERSRESPONSE']._serialized_end=676
  _globals['_GETUSERSREQUEST']._serialized_start=678
  _globals['_GETUSERSREQUEST']._serialized_end=710
  _globals['_GETUSERSRESPONSE']._serialized_start=712
  _globals['_GETUSERSRESPONSE']._serialized_end=775
  _globals['_MESSAGEOBJECT']._serialized_start=777
  _globals['_MESSAGEOBJECT']._serialized_end=903
  _globals['_SENDMESSAGEREQUEST']._serialized_start=905
  _globals['_SENDMESSAGEREQUEST']._serialized_end=963
  _globals['_SENDMESSAGERESPONSE']._serialized_start=965
  _globals['_SENDMESSAGERESPONSE']._serialized_end=1016
  _globals['_GETMESSAGEREQUEST']._serialized_start=1018
  _globals['_GETMESSAGEREQUEST']._serialized_end=1107
  _globals['_GETMESSAGERESPONSE']._serialized_start=1109
  _globals['_GETMESSAGERESPONSE']._serialized_end=1198
  _globals['_CONFIRMREADREQUEST']._serialized_start=1200
  _globals['_CONFIRMREADREQUEST']._serialized_end=1258
  _globals['_CONFIRMREADRESPONSE']._serialized_start=1260
  _globals['_CONFIRMREADRESPONSE']._serialized_end=1311
  _globals['_DELETEMESSAGEREQUEST']._serialized_start=1313
  _globals['_DELETEMESSAGEREQUEST']._serialized_end=1355
  _globals['_DELETEMESSAGERESPONSE']._serialized_start=1357
  _globals['_DELETEMESSAGERESPONSE']._serialized_end=1410
  _globals['_DELETEUSERREQUEST']._serialized_start=1412
  _globals['_DELETEUSERREQUEST']._serialized_end=1449
  _globals['_DELETEUSERRESPONSE']._serialized_start=1451
  _globals['_DELETEUSERRESPONSE']._serialized_end=1501
  _globals['_GETDATABASESREQUEST']._serialized_start=1503
  _globals['_GETDATABASESREQUEST']._serialized_end=1524
  _globals['_GETDATABASESRESPONSE']._serialized_start=1526
  _globals['_GETDATABASESRESPONSE']._serialized_end=1631
  _globals['_CHATSERVICE']._serialized_start=1706
  _globals['_CHATSERVICE']._serialized_end=2624
# @@protoc_insertion_point(module_scope)
