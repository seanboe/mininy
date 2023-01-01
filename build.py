import re
import json
import markdown
from datetime import datetime
from os import listdir
from os.path import isfile, join

site_name = "Ben's Cooking Blog"

base_path = '/Users/seanboerhout/Documents/webDev/ben-cooking-blog/'
layouts_path = 'layouts/'
posts_path = 'posts/'
dist_path = 'dist/'
card_layout_path = "card_layout.html"

class Layout_Keywords:
  TEXT_BODY = "{{text_body}}"
  POST_TITLE = "{{post_title}}"
  POST_URL = "{{post_url}}"
  POST_DATE = "{{post_date}}"
  POST_CAPTION = "{{post_caption}}"
  POST_COVER_IMAGE = "{{cover_image}}"
  CARD_LIST = "{{card_list}}"
  TAG_LIST = "{{tag_list}}"
  RELATED_POSTS_LIST = "{{related_posts}}"
  TAG_NAME = "{{tag_name}}"
  SITE_NAME = "{{site_name}}"

class Text_Colors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

  def color_wrapper(input, color):
    return color + input + '\033[0m'

all_posts = [f for f in listdir(base_path + posts_path) if isfile(join(base_path + posts_path, f))]


def convert_date(date):
  months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
  broken_date = date.split("-")
  return months[int(broken_date[0]) - 1] + " " + str(broken_date[1]) + ", " + str(broken_date[2])

def convert_to_html(markdown_text):
  converted_html = markdown.markdown(markdown_text)

  # the markdown converter converts images to the i tag
  converted_html = converted_html.replace("<i", "<img")

  def center_element(tag, html):
    element_list = re.findall(f'<{tag}(.*?)/>', html)
    for element in element_list:
      element_html = f'<{tag}{element}/>'
      html = html.replace(element_html, f'<br><div class="flex items-center justify-center">{element_html}</div><br><br>')
    return html
  
  converted_html = center_element("img", converted_html)

  # image_html_list = re.findall(r'<img(.*?)/>', converted_html)
  # for image in image_html_list:
  #   image_html = f'<img{image}/>'
  #   converted_html = converted_html.replace(image_html, f'<br><div class="flex items-center justify-center">{image_html}</div><br>')

  with open("styles.json", "r") as file: 
    styles = json.load(file)
    for style in styles:
      converted_html = converted_html.replace("<" + style, "<" + style + f" class=\"{styles[style]}\" ")

  return converted_html

def sort_posts_by_date(posts):

  date_object_list = []
  for post in posts:
    post_date_string = posts[post]["metadata"]["date"]
    post_date = datetime.strptime(post_date_string, "%B %d, %Y")
    date_object_list.append([post_date, post])

  for x in range(0, len(date_object_list)):
    recent_index = x
    for a in range(x + 1, len(date_object_list)):
      if str(date_object_list[a][0] - date_object_list[recent_index][0]).find("-"):
        recent_index = a
    temp = date_object_list[x]
    date_object_list[x] = date_object_list[recent_index]
    date_object_list[recent_index] = temp

  output = {}

  for x in range(0, len(date_object_list)):
    output[date_object_list[x][1]] = posts[date_object_list[x][1]]

  return output


# Puts all the posts into a known structure:
# {"post" : {"metadata" : {"date" : "date", "tags", ["tags"], "caption" : "caption", "cover_image" : "image_link"}, {"text_body" : "body"}}}
def preprocess_posts():
  output = {}
  for post in all_posts:
    metadata = {}
    post_body = ""
    with open(base_path + posts_path + post, "r") as text:
      text.readline()
      line = text.readline().strip()
      while line != "---":
        element = line.split(": ")
        if len(element) > 1:
          key = str(element[0].lower())
          value = str(element[1])
          if key == "date":
            metadata[key] = convert_date(value)
          elif value.find(",") >= 0:
            metadata[str(element[0])] = str(element[1]).split(", ")
          else:
            metadata[str(element[0])] = str(element[1])
        line = text.readline().strip()
      post_body = text.read()
      if "caption" not in metadata:
        metadata["caption"] = post_body[:post_body.find(" ", 70)] + "..."
      if "tags" not in metadata:
        metadata["tags"] = [""]
      if type(metadata["tags"]) is str:
        metadata["tags"] = [metadata["tags"]]
    data = {"metadata": metadata, "text_body" : convert_to_html(post_body)}
    output[post[:post.find(".")]] = data
  output = sort_posts_by_date(output)
  return output

# Returns the html for the cards for the given posts (given in the dictionary structure from preprocess_posts())
def generate_html_cards(posts):
  output = ""

  card_layout = ""
  with open(base_path + layouts_path + card_layout_path) as file:
    card_layout = file.read()

  for post in posts:
    card = card_layout
    try:
      card = card.replace(Layout_Keywords.POST_TITLE, post.replace("-", " "))
      card = card.replace(Layout_Keywords.POST_URL, f"/posts/{post}.html")
      card = card.replace(Layout_Keywords.POST_DATE, posts[post]["metadata"]["date"])
      card = card.replace(Layout_Keywords.POST_CAPTION, posts[post]["metadata"]["caption"])
      card = card.replace(Layout_Keywords.POST_COVER_IMAGE, posts[post]["metadata"]["cover_image"])
    except:
      print(Text_Colors.color_wrapper(f"Error building card for post \"{post}\"", Text_Colors.FAIL))
      continue
    output += card + " <br><br> \n "
  return output


# Processes all the posts into an easier structure to utilize later:
# {tag : {tag_url : "", post_urls : ["", ""]}}
# A list of all the tags is given by the keys of the return, and all posts are listed under their associated tags
def preprocess_tags_post(posts):
  output = {}

  for post in posts:
    for tag in posts[post]["metadata"]["tags"]:
      if tag not in output:
        # output[tag] = {"tag_url" : f"<a href=\"/tags/{tag}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{tag} </a> <br>"}
        output[tag] = {"tag_url" : convert_to_html(f"<a href=\"/tags/{tag}.html\">{tag} </a> <br>")}
        output[tag]["post_urls"] = []
      post_name = post.replace("-", " ")
      output[tag]["post_urls"].append(convert_to_html(f"<a href=\"/posts/{post}.html\">{post_name} </a> <br>"))
  return output

# Generates an all posts
def generate_posts(posts, processed_tags_posts):
  template_layout = ""
  with open(base_path + layouts_path + "post_layout.html") as file:
    template_layout = file.read()

  for post in posts:

    try:

      # Get the related posts
      related_posts = ""
      for tag in posts[post]["metadata"]["tags"]:
        for post_url in processed_tags_posts[tag]["post_urls"]:
          if post_url not in related_posts and post not in post_url:
            related_posts += post_url

      layout = template_layout
      layout = layout.replace(Layout_Keywords.SITE_NAME, site_name)
      layout = layout.replace(Layout_Keywords.POST_TITLE, post.replace("-", " "))
      layout = layout.replace(Layout_Keywords.POST_COVER_IMAGE, posts[post]["metadata"]["cover_image"])
      layout = layout.replace(Layout_Keywords.POST_DATE, posts[post]["metadata"]["date"])
      layout = layout.replace(Layout_Keywords.TEXT_BODY, posts[post]["text_body"])
      layout = layout.replace(Layout_Keywords.RELATED_POSTS_LIST, related_posts)

      with open(base_path + dist_path + "posts/" + f"{post}.html", "w") as file:
        file.write(layout)  

    except:
      print(Text_Colors.color_wrapper(f"Error building page for post \"{post}\"", Text_Colors.FAIL))


# Generates the tag pages
def generate_tags(posts, processed_tags_posts):
  
  template = ""
  with open(base_path + layouts_path + "tag_layout.html") as file:
    template = file.read()

  for tag in processed_tags_posts:
    tag_page = template
    associated_posts = {}
    for post_url in processed_tags_posts[tag]["post_urls"]:
      post = re.findall("/posts/(.*?).html", post_url)[0]
      associated_posts[post] = posts[post]

    # Build the cards
    cards = generate_html_cards(associated_posts)

    tag_list = ""
    for tag_element in processed_tags_posts:
      if tag_element is not tag:
        tag_list += processed_tags_posts[tag_element]["tag_url"]

    try:
      tag_page = tag_page.replace(Layout_Keywords.SITE_NAME, site_name)
      tag_page = tag_page.replace(Layout_Keywords.TAG_NAME, tag)
      tag_page = tag_page.replace(Layout_Keywords.CARD_LIST, cards)
      tag_page = tag_page.replace(Layout_Keywords.TAG_LIST, tag_list)
    except:
      print(Text_Colors.color_wrapper(f"Error building page for tag \"{tag}\"", Text_Colors.FAIL))
    
    with open(base_path + dist_path + f"tags/{tag}.html", "w") as file:
      file.write(tag_page)


def main():

  # Some setup stuff
  processed_posts = preprocess_posts()
  processed_tags_posts = preprocess_tags_post(processed_posts)

  tag_list = ""
  for tag in processed_tags_posts:
    tag_list += processed_tags_posts[tag]["tag_url"]


  # Move the tailwindcs styles file to the dist folder
  tailwind_styles = ""
  with open(base_path + "tailwind-styles.js") as file:
    tailwind_styles = file.read()
  with open(base_path + dist_path + "tailwind-styles.js", "w") as file:
    file.write(tailwind_styles)


  # Build the index page
  index = ""
  with open(base_path + layouts_path + "index_layout.html") as file:
    layout = file.read()
    index = layout.replace(Layout_Keywords.SITE_NAME, site_name)
    index = index.replace(Layout_Keywords.CARD_LIST, generate_html_cards(processed_posts))
    index = index.replace(Layout_Keywords.TAG_LIST, tag_list)
  with open(base_path + dist_path + "index.html", "w") as file:
    file.write(index)

  # Generate the posts under /dist/posts/
  generate_posts(processed_posts, processed_tags_posts)
  generate_tags(processed_posts, processed_tags_posts)


  sort_posts_by_date(processed_posts)


if __name__ == "__main__":
  main()