from app import db


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    initial_url = db.Column(db.String(200), nullable=False, unique=True)
    uuid = db.Column(db.String(36), nullable=False, unique=True)
    protocol = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(200), nullable=False)
    domain_zone = db.Column(db.String(200), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    parameters = db.Column(db.JSON(), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'protocol': self.protocol,
            'domain': self.domain,
            'domain_zone': self.domain_zone,
            'path': self.path,
            'parameters': self.parameters
        }
