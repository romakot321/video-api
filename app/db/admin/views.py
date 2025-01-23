from app.db.tables import Video
from sqladmin import ModelView


class VideoView(ModelView, model=Video):
    column_list = "__all__"
    column_searchable_list = [Video.status, Video.user_id, Video.id]
    column_sortable_list = [Video.created_at, Video.finished_at]
    column_default_sort = [(Video.created_at, True)]

