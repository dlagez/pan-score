from app import create_app
from app.services.rating_aggregation import refresh_share_link_scores


def main():
    app = create_app()
    with app.app_context():
        updated = refresh_share_link_scores()
        print(f"updated_share_links={updated}")


if __name__ == "__main__":
    main()
