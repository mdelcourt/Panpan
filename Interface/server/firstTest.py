from wsgiref.simple_server import make_server
from tg import expose, TGController, AppConfig
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates

#import templates

class RootController(TGController):
  @expose('templates.test')
  def test(self):
      """Handle the 'about' page."""
      return dict(message='salut')

config = AppConfig(minimal=True,root_controller=RootController())
config.renderers = ['kajiki']
application = config.make_wsgi_app()

print "Serving on port 8080..."
httpd = make_server('', 8080, config.make_wsgi_app())
httpd.serve_forever() 

