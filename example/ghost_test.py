from ghost import Ghost
ghost = Ghost()
with ghost.start() as session:
    page, extra_resources = session.open("http://test.baoda8.com/login")
    session.set_field_value(selector='[mame~=user]', value='di.xiao@socialcredits.cn')
    session.set_field_value(selector='[name~=userPassword]', value='xiaodidi')
    session.click(selector="")