# wwpbat

**This code comes with absolutely no warrany. Don't use it!**

This is my White Wall Photo Book alignment tool.
Accurately laying out many pages of a photo book can be a bit of a pain.
[White Wall](https://www.whitewall.com/) photo book layouts are stored in JSON,
so we can fiddle with the data.


## Data location

In my Mac OS system, photo books are stored in
```
/Users/<username>/Library/Containers/de.whitewall.pgx.osx/Data/Library/Application Support/de.whitewall.pgx.osx/File Storage/unprotectedFileStorage/projects
``` 
(your location may vary, especially because of the `de.` location prefix).

This folder contains an `index.json`, which is an index to the existing photo book projects. Projects are identified with a long hash value. Per project there is a `.base64` file 
containing a project thumbnail and a `.json` file containing the photo book layout.

The photos themselves are in
```
/Users/<username>/Library/Containers/de.whitewall.pgx.osx/Data/Library/Application Support/de.whitewall.pgx.osx/Retained Images/<project hash>
```

## The process

1. Create a new photo book project in the White Wall desktop app
2. Insert all images that you want in the photo book, put them on the pages
   in roughly the right location.
3. Close the project in the White Wall app
4. Find the projects `.json`, make a backup copy (just to be safe).
5. Run the `wwpbat` tool on the project `.json` (inserting paths as appropriate):
    ```
    python wwpbat.py <project file>.json
    ```
   The `.json` will be modified in-place, a backup copy with the current time stamp
   appended to the file name will be created (so you may accumulate a lot of those
   backup copies).
6. Re-open the project in the White Wall app
   
   
## Layout logic

Image edges are snapped to a coarse grid spanning the page.
The aspect ratio of the images is retained.
The dimension (horizontal or vertical) for which the image edges (including margins)
are closest on average to their respective closest grid lines, wins and
determines the image size.

Along the winning dimension, both (i.e. upper and lower _or_ left and right) edges
are snapped. Along the losing dimension, the image is snapped to the center or an
outer edge is snapped to the page edge, whichever requires less translation.

Then, images are reduced in size to take into account page margins 
and inter-image spacing.

The cover (first page object in the file) is not modified.

Only objects of type `PICTURE` are modified, across all layers.


## Settings

In the header of `wwpbat.py` there are various settings to make, like adjusting margins
and spacing between images, as well as the number of grid lines on the page.


