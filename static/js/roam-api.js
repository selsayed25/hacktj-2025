/**
 * @typedef {Object} Chat
 * @property {string} id
 * @property {string} started - The ISO timestamp the chat started
 * @property {string} [group] - The group ID, if this is a group chat
 * @property {string} name - The descriptive name for the chat
 */

/**
 * Lists all accessible chats, which consist of DMs, MultiDMs, and Channels
 * your bot has been added to, in addition to all public groups regardless of
 * membership.
 *
 * Chats are returned in reverse chronological order of the chat's start
 * timestamp, so the first page of results contains the most recently started
 * chats.
 *
 * @param {string} apiKey
 * @param {number} [limit] - The number of chats to return per response. Between 1 and 100, inclusive.
 * @param {string} [cursor] - A `nextCursor` value from an earlier response.
 * @returns {Promise<{ chats?: Array<Chat> }>}
 */
const listChats = async (apiKey, limit, cursor) => {
    return await makeRequest(apiKey, "GET", "chat.list", { limit, cursor });
  };
  
  /**
   * @typedef {Object} Message
   * @property {string} type
   * @property {string} sender
   * @property {string} chat
   * @property {number} [threadTimestamp]
   * @property {number} timestamp
   * @property {string} text
   *
   * TODO: add more properties
   */
  
  /**
   * List messages in a chat, filtered by date range.
   *
   * When no parameters are provided, the most recent chats are returned, sorted in reverse chronological order. This is equivalent to specifying `before` as NOW and leaving `after` unspecified.
   *
   * If `after` is specified, the results are sorted in forward chronological order.
   *
   * @param {string} apiKey
   * @param {string} chatId - The chat address to fetch information for
   * @param {number} [threadTimestamp] - Read replies of the message with this timestamp
   * @param {string} [after] - The datetime to begin listing timestamps, in YYYY-MM-DD or RFC-3339 normal. Defaults to "no filter"
   * @param {string} [before] - The datetime until which to list transscripts, same format as `after`. Defaults to "now".
   * @param {string} [cursor] - Cursor to continue listing results
   * @param {number} [limit] - Limit the number of messages returned. Between 10 and 250, inclusive.
   *
   * @returns {Promise<{ chat: string; nextCursor?: string; messages: Array<Message> {>}
   */
  const getChatMessages = async (
    apiKey,
    chatId,
    threadTimestamp,
    after,
    before,
    cursor,
    limit
  ) => {
    return await makeRequest(apiKey, "GET", "chat.history", {
      chat: chatId,
      threadTimestamp,
      after,
      before,
      cursor,
      limit,
    });
  };
  
  /**
   * Post a markdown-formatted text message to a chat.
   *
   * @param {string} apiKey
   * @param {string} chatId
   * @param {string} text
   * @param {number} [threadTimestamp] - Set this to reply to a message in a Group.
   * @param {boolean} [sync] - If set, the post will be performed synchronously and its timestamp returned.
   */
  const postChat = async (apiKey, chatId, text, threadTimestamp, sync) => {
    return await makeRequest(apiKey, "POST", "chat.post", {
      chat: chatId,
      threadTimestamp,
      text,
      sync,
    });
  };
  
  /**
   * @typedef {Object} Knock
   * @property {string} id
   * @property {string} name
   * @property {string} instructions
   * @property {string} target
   * @property {string} [output]
   */
  
  /**
   * Tells your bot to knock on someone's door.
   *
   * @param {string} apiKey - Your API Key
   * @param {string} email - Email of the person to visit.
   * @param {string} name - The name you want your bot to show up as.
   * @param {string} instructions - System instructions passed to the LLM
   * @returns {Promise<Knock>} The created knock
   */
  const createKnock = async (apiKey, email, name, instructions) => {
    return await makeRequest(apiKey, "POST", "bot.knock.create", {
      target: email,
      name,
      instructions,
    });
  };
  
  /**
   * Checks the status of a knock.
   *
   * @param {string} apiKey - Your API Key
   * @param {string} knockId - The ID of the knock record to retrieve
   * @returns {Promise<Knock>} The specified knock
   */
  const checkKnock = async (apiKey, knockId) => {
    return await makeRequest(apiKey, "GET", "bot.knock.info", { id: knockId });
  };
  
  /**
   * Makes an arbitrary request to the Roam API.
   */
  const makeRequest = async (apiKey, method, path, body) => {
    let url = new URL(path, ROAM_BASE_URL).toString();
    if (method === "GET") {
      url = `${url}?${new URLSearchParams(body)}`;
    }
    const response = await fetch(url, {
      body: method === "POST" ? JSON.stringify(body) : undefined,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      method,
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return await response.json();
  };
  
  /**
   * NOTE: If this code runs on a server, you should uncomment the following:
   */
  // const ROAM_BASE_URL = new URL("https://api.ro.am/v0/");