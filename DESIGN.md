# LitFlaneur Design Document

Inspired by Walter Benjamin's notion of constellation, this web application provides a tool to faciliate the core practices in academia: reading, writing, and thinking. See [video introduction](https://youtu.be/qB_iIyjBok4).

## Structure

1. Log In `/login`
   1. Check for missing fields
   2. Check for username
   3. Check for mateched password
2. Register `/register`
3. Main `/constellation`
   1. Visualize the information in database
4. Create
   1. Planet `/add-node`
      * Name `name`
      * Summary `summary`
      * Content `content`
      * Citation
        * Last Name of Author `author`
        * Year of Publish `date`
        * Title `title`
      * Category `category`
        * Claim
        * Reason
        * Evidence
        * Warrant
        * Response
   2. Gravitation `/add-link`
      * Source `source`
      * Target `target`
5. Dashboard `/dashboard`
   1. Search `/search`
   2. Card
      * Information
      * Delete `/manage`
6. Manifesto `/manifesto`
7. Security `/password`
   1. Check for matched password
   2. Confirm password
8. Log Out `/logout`

## Implementation

* 3.1: Introduce an open-source library to visualize the information stored in the batabase as a diagram, see https://gallery.pyecharts.org/#/Graph/graph_with_options and https://echarts.apache.org/examples/zh/editor.html?c=graph-webkit-dep. In the provided library, nodes and links are hard coded. To make it possible to add and delete from the front end, use `SELECT` SQL command in `app.py` to pass infromation from database to the main page. Customize the parameters. Use call-after function to show more information in the tooltip.
* 4.1: Use `INSERT` SQL command to pass inputs to the back end and store them into the database.
* 4.2: Introduced an open-source library to show a dropdown autocompleting list below the input bar to promote the user experience, see https://select2.org/getting-started/basic-usage. Use `SELECT` SQL command to pass values to the front end and use jinja to list them all in HTML.
* 5.1: Use `GET` HTTP request in `/search` and `SELECT` SQL command to search for `planet` in the database whose name includes the inputted keyword. 
* 5.2: Use `GET` HTTP request in `/dashboard` to list the information of each `planet` using jinja. Use `GET` HTTP request in `/manage` to pass value with URL to let the back end know which card's `delete` button is clicked, thus deleting the corresponding entry in database using `DELETE` SQL command.

## Ways Forward

* 3.1: Show rich text in the tooltip. Link nodes to dashboard.
* 4: Embed these functions into the main page with a pop-up window. Create the unique index of each `planet` in the database to make it more convenient for users to name a `planet`.
* 4.1: Add more restrictions in the back end to secure the correct format of inputs. 
* 4.2: Show `summary` of each `planet` in the dropdown list to remind users of the contents. 
* 5.2: Add an edit function by using `UPDATE` SQL command. Show pop-up window to prompt users to input or reconsider.
* Enable users create multiple `constellation` by adding one more field in the tables in database to filter the specific `constellation`. Add a new page  `/gallery` to show all `constellation` created by the user.
* Create a new page `universe` to make it possible for online users to create shared `constellation`, which seems to be a visualized Wikipedia.

## Acknowledgement

Special thanks to

* Rob Walker, Harvard University
* Qinyao He, Columbia University
* Hongbo Wen, Tsinghua University
* Zhichun Li, Tsinghua University

More references

* https://zhuanlan.zhihu.com/p/133533187
* https://www.bilibili.com/video/BV1CK411n71L?from=search&seid=2706678234905293695&spm_id_from=333.337.0.0
* http://www.crazyant.net/2419.html?utm_source=tuicool&utm_medium=referral
* https://cs50.stackexchange.com/questions/25136/pset7-index-html-adding-buy-sell-button-which-linked-to-stock-respectively
* Previous lecture notes, distribution code of labs and problem sets.
