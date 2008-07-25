from django.db        import models
from django.db.models import permalink

from articles.models      import Article
from announcements.models import Announcement

from datetime import date, timedelta
import scrapers.sharples


class Issue(models.Model):
    """An issue of the paper."""
    
    date    = models.DateField(default=date.today)
    menu    = models.ForeignKey('Menu', null=True)
    weather = models.TextField(blank=True)
    events  = models.TextField(blank=True)
    
    def add_article(self, article):
        """Appends an article to this issue."""
        IssueArticle.objects.create(issue=self, article=article)
    
    def add_announcement(self, announcement):
        """Appends an announcement to this issue."""
        IssueAnnouncement.objects.create(issue=self, announcement=announcement)
    
    def __unicode__(self):
        return self.date.strftime("%a, %d %B %Y")
    
    @permalink
    def get_absolute_url(self):
        a = [str(x) for x in (self.date.year, self.date.month, self.date.day)]
        return ('issues.views.for_date', a)
    

class IssueArticle(models.Model):
    """An issue's having an article. Includes position metadata."""
    
    issue    = models.ForeignKey(Issue, related_name="articles")
    article  = models.ForeignKey(Article, related_name="issues")
    
    class Meta:
        order_with_respect_to = 'issue'
        unique_together = ('issue', 'article')
    
    def __unicode__(self):
        return u"%s on %s" % (self.article.slug, self.issue.date)
    

class IssueAnnouncement(models.Model):
    """An issue's having an announcement. Includes position metadata."""
    
    issue        = models.ForeignKey(Issue, related_name="announcements")
    announcement = models.ForeignKey(Announcement, related_name="issues")
    
    class Meta:
        order_with_respect_to = 'issue'
        unique_together = ('issue', 'announcement')
    
    def __unicode__(self):
        return u"%s on %s" % (self.announcement.slug, self.issue.date)
    

class MenuManager(models.Manager):
    def for_today(self):
        return self.get_or_parse(tomorrow=False)
    
    def for_tomorrow(self):
        return self.get_or_parse(tomorrow=True)
    
    def get_or_parse(self, tomorrow=False):
        """
        Returns the Sharples menu object for today/tomorrow, creating a
        new one (by parsing it from the XML feed) if necessary.
        """
        try:
            day = date.today()
            if tomorrow:
                day += timedelta(days=1)
            return self.get(date=day)
        
        except self.model.DoesNotExist:
            menu = scrapers.sharples.get_menu(tomorrow=tomorrow)
            return Menu.objects.create(
                date = date.today(),
                closed  = menu['closed'],
                message = menu['message'],
                lunch   = menu['lunch'],
                dinner  = menu['dinner']
            )
    


class Menu(models.Model):
    """The menu at Sharples for a given day."""
    
    date = models.DateField(default=date.today)
    
    closed  = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    
    lunch  = models.TextField(blank=True)
    dinner = models.TextField(blank=True)
    
    objects = MenuManager()
    
    def __unicode__(self):
        return self.date.strftime("%m/%d/%Y")
    
