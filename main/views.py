from django.shortcuts import render

from django.http import HttpResponse


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /\n",
        content_type="text/plain"
    )


def sitemap_xml(request):
    return HttpResponse(
        """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://nstyranets.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://nstyranets.com/about_me/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
""",
        content_type="application/xml"
    )


def home(request):
    return render(request, 'main/home.html')


def about_me(request):
    return render(request, 'main/about_me.html')
