import arrow
utc = arrow.utcnow()
local=utc.to('Asia/Taipei')
print(type(local.format('HH:mm:ss')))