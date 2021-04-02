# Demo (Concept)

```py
# display_image_demo.py

with Application() as app:
    with QLabel() as label:
        label.geometry = (x, y, w, h)
    
    with QPixmap(filepath := os.path.join(...)) as pxmap:
        label.set_pixmap(pxmap)
        label.move(10, 10)
    
    with app.on_completed:
        app.start()

```
