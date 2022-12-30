import re
import json
import markdown
from os import listdir
from os.path import isfile, join

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
  with open("styles.json", "r") as file: 
    styles = json.load(file)
    for style in styles:
      try: 
        converted_html = converted_html.replace("<" + style, "<" + style + f" class=\"{styles[style]}\" ")
      except:
        pass
  return converted_html

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
  return output

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
        output[tag] = {"tag_url" : f"<a href=\"/tags/{tag}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{tag} </a> <br>"}
        output[tag]["post_urls"] = []
      output[tag]["post_urls"].append(f"<a href=\"/posts/{post}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{post} </a> <br>")
  return output

# def generate_tag_list(posts):
#   output = ""
#   for post in posts:
#     for tag in posts[post]["metadata"]["tags"]:
#       if tag not in output:
#         output += f"<a href=\"/tags/{tag}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{tag} </a> <br>"
#   return output

# def generate_post_list(posts, tag):
#   output = ""
#   for post in posts:
#     if tag in posts[post]["metadata"]["tags"]:
#       output += f"<a href=\"/posts/{post}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{post} </a> <br>"

# Generates an individual post
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
      layout = layout.replace(Layout_Keywords.POST_TITLE, post.replace("-", " "))
      layout = layout.replace(Layout_Keywords.POST_COVER_IMAGE, posts[post]["metadata"]["cover_image"])
      layout = layout.replace(Layout_Keywords.POST_DATE, posts[post]["metadata"]["date"])
      layout = layout.replace(Layout_Keywords.TEXT_BODY, posts[post]["text_body"])
      layout = layout.replace(Layout_Keywords.RELATED_POSTS_LIST, related_posts)

      with open(base_path + dist_path + "posts/" + f"{post}.html", "w") as file:
        file.write(layout)  

    except:
      print(Text_Colors.color_wrapper(f"Error building page for post \"{post}\"", Text_Colors.FAIL))

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
    index = layout.replace(Layout_Keywords.CARD_LIST, generate_html_cards(processed_posts))
    index = index.replace(Layout_Keywords.TAG_LIST, tag_list)
  with open(base_path + dist_path + "index.html", "w") as file:
    file.write(index)

  # Generate the posts under /dist/posts/
  generate_posts(processed_posts, processed_tags_posts)










  # print(preprocess_tag_post(preprocess_posts()))











# def main():

#   layout_body_standard = ""
#   layout_keywords = []
#   with open(base_path + "letter-layout.html", "r") as layout:
#     layout_body_standard = layout.read()
#     layout_keywords = re.findall(r'{{(.*?)}}', layout_body_standard)
  
#   letter_files = [f for f in listdir(base_path + letters_path) if isfile(join(base_path + letters_path, f))]

#   for letter in letter_files:
#     text_body = ""
#     layout_body = layout_body_standard
#     metadata = {}
#     with open(base_path + letters_path + letter, "r") as text:
#       text.readline()
#       line = text.readline().strip()
#       while line != "---":
#         element = line.split(" ")
#         metadata[str(element[0])[:-1]] = str(element[1])
#         line = text.readline().strip()
      
#       text_body = text.read()

#     layout_body = layout_body.replace("{{text_body}}", text_body)
#     for keyword in layout_keywords:
#       if keyword == "text_body":
#         continue
#       try:
#         layout_body =layout_body.replace("{{" + keyword + "}}", metadata[keyword])
#       except:
#         print(f"Error in building file \"{letter}\"")

#     with open(base_path + dist_path + letter[:letter.find(".")] + ".html", "w") as dist_file:
#       dist_file.write(layout_body)

#     print(f"Build completed!   \"{letter}\"")

if __name__ == "__main__":
  main()