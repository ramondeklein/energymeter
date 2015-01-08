from database import Database;

class Settings:
  # String 'get' method
  @staticmethod
  def get_string(setting):
    cur = Database.cursor()
    cur.execute("SELECT value FROM settings WHERE setting = %s", setting)
    return cur.fetchone()

  # String 'set' method
  @staticmethod
  def set_string(setting, value):
    cur = Database.cursor()
    cur.execute("INSERT INTO settings(setting,value) VALUES(%s,%s) ON DUPLICATE KEY UPDATE value=%s", setting, value, value)
    Database.commit()

  # Boolean 'get' method
  @staticmethod
  def get_bool(setting):
    value = Settings.get_string(setting)
    if not value:
      return False
    value = value[0].lower()
    return False if (value == 'no') or (value == 'false') or (value == '0') else True

  # Boolean 'set' method
  @staticmethod
  def set_bool(setting, value):
    Settings.set_string(setting, 'true' if value else 'false')

  # Integer 'get' method
  @staticmethod
  def get_int(setting):
    value = Settings.get_string(setting)
    if not value:
      return 0
    try:
      return int(value)
    except:
      return 0

  # Integer 'set' method
  @staticmethod
  def set_int(setting, value):
    Settings.set_string(setting, value)
