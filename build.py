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
      card = card.replace(Layout_Keywords.POST_TITLE, post)
      card = card.replace(Layout_Keywords.POST_URL, post + ".html")
      card = card.replace(Layout_Keywords.POST_DATE, posts[post]["metadata"]["date"])
      card = card.replace(Layout_Keywords.POST_CAPTION, posts[post]["metadata"]["caption"])
      card = card.replace(Layout_Keywords.POST_COVER_IMAGE, posts[post]["metadata"]["cover_image"])
    except:
      print(Text_Colors.color_wrapper(f"Error building card for post \"{post}\"", Text_Colors.FAIL))
      continue
    output += card + " <br><br> \n "
  return output

def generate_tag_list(posts):
  output = ""
  for post in posts:
    for tag in posts[post]["metadata"]["tags"]:
      if tag not in output:
        output += f"<a href=\"/tags/{tag}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{tag} </a> <br>"
  return output

def generate_post_list(posts, tag):
  output = ""
  for post in posts:
    if tag in posts[post]["metadata"]["tags"]:
      output += f"<a href=\"/posts/{post}.html\" class=\"text-lg transition-all duration-200 underline decoration-light-blue hover:decoration-transparent\">{post} </a> <br>"

def main():

  # Process the index file
  print(preprocess_posts())
  with open(base_path + "test.html", "w") as file:
    file.write(generate_tag_list(preprocess_posts()))

  index = ""
  with open(base_path + layouts_path + "index_layout.html") as file:
    layout = file.read()
    processed_posts = preprocess_posts()
    index = layout.replace(Layout_Keywords.CARD_LIST, generate_html_cards(processed_posts))
    index = index.replace(Layout_Keywords.TAG_LIST, generate_tag_list(processed_posts))
  with open(base_path + dist_path + "index.html", "w") as file:
    file.write(index)











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