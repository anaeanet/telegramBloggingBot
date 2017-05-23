from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class IdleState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def __init__(self, context, user_id, chat_id=None, message_id=None):
        super().__init__(context)

        # TODO serialize/deserialze them in sqldbwrapper
        self.__message_id = message_id

        if chat_id is not None:
            self.show_menu(user_id, chat_id, message_id=message_id)

    @property
    def message_id(self):
        return self.__message_id

    @message_id.setter
    def message_id(self, message_id):
        self.__message_id = max(self.__message_id, message_id)

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = [{"text": "CREATE a draft", "callback_data": "/createdraft"}]
        if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
            reply_options.append({"text": "UPDATE a draft", "callback_data": "/updatedraft"})
            reply_options.append({"text": "DELETE a draft", "callback_data": "/deletedraft"})
            # TODO
            #reply_options.append({"text": "PREVIEW a draft", "callback_data": "/previewdraft"})
            #reply_options.append({"text": "PUBLISH a draft", "callback_data": "/publishdraft"})

        message_text = "What do you want to do?"
        if message_id is not None:
            self.context.edit_message_text(chat_id, message_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))
        else:
            self.context.send_message(chat_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))

    def process_message(self, user_id, chat_id, text):
        # welcome message
        if text in ["/start"]:
            self.context.send_message(chat_id,
                                            "Welcome to your mobile blogging bot!"
                                            + "\r\n"
                                            + "\r\n"
                                            + "I am here to help you create new blog posts or manage existing ones. "
                                            + "Just follow the interactive menu!"
                                            , parse_mode=ParseMode.MARKDOWN.value)

        next_state = IdleState(self.context, user_id, chat_id=chat_id)
        self.context.set_user_state(user_id, next_state)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        if len(command_array) > 0:

            if command_array[0] == "/mainmenu":
                next_state = IdleState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/createdraft":
                from packages.states.createdraftstate import CreateDraftState
                next_state = CreateDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/updatedraft":
                from packages.states.updatedraft import UpdateDraftState
                next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/deletedraft":
                from packages.states.deletedraftstate import DeleteDraftState
                next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/previewdraft":
                # TODO
                None
            elif command_array[0] == "/publishdraft":
                # TODO
                None

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            self.process_message(user_id, chat_id, text)

        elif update_type == "callback_query":
            self.context.answer_callback_query(update[update_type]["id"])

            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            self.process_callback_query(user_id, chat_id, message_id, data)

        else:   # unsupported update type
            print("unsupported update type:", update_type) # TODO change to log rather than print
