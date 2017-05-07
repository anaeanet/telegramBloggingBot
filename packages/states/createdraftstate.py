from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class CreateDraftState(AbstractState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, chat_id=None, user_id=None):
        super().__init__(context)

        if chat_id is not None:
            self.get_context().send_message(chat_id, "What is the *title* of your new draft?"
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_keyboard(None))

    def process_update(self, update):
        print(update)

        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            if text:    # text message

                if text in ["/start", "/help"]:
                    self.get_context().send_message(chat_id,
                                                    "Welcome to your mobile blogging bot! I am here to help you create new blog posts or update existing ones while you are on the go."
                                                    + "\r\n"
                                                    + "\r\n" + "You can control me by the following commands:"
                                                    + "\r\n"
                                                    + "\r\n" + "*Drafts - Unpublished blog posts*"
                                                    + "\r\n" + "/createdraft - begin a new draft"
                                                    + "\r\n" + "/updatedraft - continue working on a draft"
                                                    + "\r\n" + "/deletedraft - delete a draft"
                                                    , parse_mode=ParseMode.MARKDOWN.value
                                                    , reply_markup=telegram.build_keyboard(None))
                    from packages.states.idlestate import IdleState
                    self.get_context().set_user_state(user_id, IdleState(self.get_context()))
                    return

                # TODO implement all other commands here

                elif "entities" not in update[update_type]: # plain text message, does not contain bot_commands, urls, ...
                    self.get_context().add_post(user_id, text)
                    self.get_context().send_message(chat_id, "Successfully created draft '*" + text + "*'"
                                                    , parse_mode=ParseMode.MARKDOWN.value
                                                    , reply_markup=telegram.build_keyboard(None))
                    from packages.states.idlestate import IdleState
                    self.get_context().set_user_state(user_id, IdleState(self.get_context()))
                    return

            self.get_context().send_message(chat_id, "Unrecognized command or message!"
                                            + "\r\n" + "Send /help to see available commands."
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_keyboard(None))

        else:
            print("un-implemented update type:", update)