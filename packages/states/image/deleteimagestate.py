from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class DeleteImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Lets the user select an image for deletion.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:
            message = "Which <b>image</b> do you want to <b>delete</b> from draft <b>" + post.title + "</b>?"

        return message

    @property
    def callback_options(self):

        # add buttons to return to update option menu, draft list
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # show deletion and preview button for every image currently assigned to draft
        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:

            if post.title_image is not None:
                reply_options.append({"text": "[TITLE] " + post.title_image.name, "callback_data": "/deletepostimage " + str(post.title_image.id)})
                reply_options.append({"text": "preview", "callback_data": "/previewpostimage " + str(post.title_image.id)})

            for image in post.gallery.images:
                reply_options.append({"text": image.name, "callback_data": "/deletepostimage " + str(image.id)})
                reply_options.append({"text": "preview", "callback_data": "/previewpostimage " + str(image.id)})

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/deletepostimage <image_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/deletepostimage":

            image_id = command_array[1]

            # check if previously selected post still exists
            post = self.bot.persistence.get_post(self.post_id)
            if post is not None:

                deleted_image = self.bot.persistence.delete_post_image(post.id, image_id)

                # image removal successful
                if deleted_image is not None:
                    self.bot.edit_message_text(chat_id, message_id
                                               , "Image <b>" + deleted_image.name + "</b> has been <b>deleted</b> from draft <b>" + post.title + "</b>."
                                               , parse_mode=ParseMode.HTML.value)
                # image removal not successful
                else:
                    self.bot.edit_message_text(chat_id, self.message_id
                                               , "It seems the image you selected no longer exists..."
                                               , parse_mode=ParseMode.HTML.value)

                # show remaining images for deletion
                post_images = post.gallery.images + ([post.title_image] if post.title_image is not None else [])
                if len(post_images) - (1 if deleted_image is not None else 0) > 0:
                    next_state = DeleteImageState(self.bot, user_id, post.id, chat_id=chat_id)
                # no remaining images -> automatically go back to update option menu
                else:
                    next_state = SelectDraftUpdateState(self.bot, user_id, self.post_id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.bot.send_message(chat_id
                                      , "It seems the draft you selected no longer exists..."
                                      , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.bot.persistence.get_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import DeleteDraftState
                    next_state = DeleteDraftState(self.bot, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.bot, user_id, chat_id=chat_id)

        # only accept "/previewpostimage <image_id>" callback queries
        elif len(command_array) == 2 and command_array[0] == "/previewpostimage":

            image_id = command_array[1]

            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            # check if previously selected post still exists
            post = self.bot.persistence.get_post(self.post_id)
            if post is not None:

                preview_image = None
                for image in post.gallery.images + ([post.title_image] if post.title_image is not None else []):
                    # ignore "wrong" images
                    if str(image.id) != str(image_id):
                        continue
                    else:
                        preview_image = image

                # image found -> preview
                if image is not None:
                    self.bot.send_photo(chat_id, image.thumb_id if image.thumb_id else image.file_id, caption=image.caption)
                # image not found
                else:
                    self.bot.edit_message_text(chat_id, self.message_id
                                               , "It seems the image you selected no longer exists..."
                                               , parse_mode=ParseMode.HTML.value)

                next_state = DeleteImageState(self.bot, user_id, self.post_id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.bot.send_message(chat_id
                                      , "It seems the draft you selected no longer exists..."
                                      , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.bot.persistence.get_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import DeleteDraftState
                    next_state = DeleteDraftState(self.bot, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.bot, user_id, chat_id=chat_id)
        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
