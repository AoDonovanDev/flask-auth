from models import User, Feedback, db
from app import app

app.app_context().push()

db.drop_all()
db.create_all()

u = User.register(username='trillbo', password='trillbo', first_name='andrew', last_name='donovan', email='aodonovanmusic@gmail.com')

db.session.add(u)
db.session.commit()

f = Feedback(title='hey', content='here goes', username='trillbo')

db.session.add(f)
db.session.commit()