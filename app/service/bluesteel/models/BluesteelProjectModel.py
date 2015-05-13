""" BlueSteelProject model """

from django.db import models

class BluesteelProjectEntry(models.Model):
    """ BlueSteel Project """
    archive = models.CharField(default='', max_length=50)
    name = models.CharField(default='', max_length=50)
    git_project = models.ForeignKey('gitrepo.GitProjectEntry', related_name='bluesteel_git_project')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Bluesteel Project archive:{0}, name:{1}, git_project{2}'.format(
            self.archive,
            self.name,
            self.git_project.id
        )

