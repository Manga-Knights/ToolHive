from functools import partial

def connect_scroll_sync(view1, view2):
    """Synchronize scrollbars between two views without infinite recursion."""
    updating = {"horizontal": False, "vertical": False}

    def sync_scroll(orientation: str, value: int, source_view):
        if updating[orientation]:
            return  # prevent feedback loop

        updating[orientation] = True
        source_scrollbar = (
            source_view.verticalScrollBar()
            if orientation == "vertical"
            else source_view.horizontalScrollBar()
        )

        # Compute fraction of scroll position (0–1)
        fraction = value / source_scrollbar.maximum() if source_scrollbar.maximum() else 0

        for target in (view1, view2):
            if target == source_view:
                continue
            target_scrollbar = (
                target.verticalScrollBar()
                if orientation == "vertical"
                else target.horizontalScrollBar()
            )
            target_scrollbar.setValue(int(fraction * target_scrollbar.maximum()))

        updating[orientation] = False

    # Use partial to avoid late-binding issues with lambdas
    for view in (view1, view2):
        view.horizontalScrollBar().valueChanged.connect(
            partial(sync_scroll, "horizontal", source_view=view)
        )
        view.verticalScrollBar().valueChanged.connect(
            partial(sync_scroll, "vertical", source_view=view)
        )


def connect_zoom_sync(view1, view2):
    """Synchronize zoom / transform between two image views (bi-directional)."""

    def sync_transform(transform, target_view):
        # This assumes your ImageView class defines `set_transform()`
        target_view.set_transform(transform)

    # Note: Signal name corrected from 'tranformChanged' → 'transformChanged'
    view1.transformChanged.connect(partial(sync_transform, target_view=view2))
    view2.transformChanged.connect(partial(sync_transform, target_view=view1))
