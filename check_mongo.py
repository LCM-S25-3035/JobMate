from app import create_app

app = create_app()
with app.app_context():
    print('MongoDB connected:', hasattr(app, 'mongo_db'))
    if hasattr(app, 'mongo_db'):
        try:
            # Try to list collections to test connectivity
            collections = app.mongo_db.list_collection_names()
            print('MongoDB collections:', collections)
        except Exception as e:
            print('MongoDB error:', str(e))
