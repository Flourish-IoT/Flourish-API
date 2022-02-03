from flask_restx import fields, Model

DeviceModel = Model('Device', {
	'id': fields.Integer(attribute='device_id'),
	'deviceType': fields.String(attribute='device_type'),
	'deviceState': fields.String(attribute='device_state'),
	'model': fields.String,
	'name': fields.String
})

DeviceDetailModel = Model('DeviceDetails'
	''
)