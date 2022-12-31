# Minimy

I got bored towards the end of winter break and one of my friends wanted a blog, so I decided to make one for him from the ground up... aka without using any frameworks. All the posts are manually built using page layouts under the `/layouts/` folder by `build.py`. Give the blog your own title by editing `site_name` in `build.py` To add posts, make a markdown file under `/posts/` and include the correct frontmatter. The tags, tag pages, and everything else will be generated for your as static html files in `/dist/`. To deploy, just deploy the `/dist/` folder without any frameworks enabled!

Also, the blog uses GraphComment for the commenting box/service. To use your own comments, make a graphcomment account and fill in the correct graphcomment_id.


Dist
  - index.html
  - Posts
    - Indpendent Posts
  - Tags
    - Indendent Tag Pages
Layouts
  - [various layouts]
Posts