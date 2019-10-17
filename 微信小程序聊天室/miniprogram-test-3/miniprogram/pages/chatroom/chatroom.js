wx.cloud.init()
const db = wx.cloud.database()
const chatroomCollection = db.collection('chatroom')
Page({
  /**
   * 页面的初始数据
   */
  data: {
    userInfo: null, // 存储当前用户信息
    textInputValue: '', // 存储输入内容
    chats: [], // 存储聊天记录
    openId: '', // 当前用户openid
    current_question:"xasxsaxasx"
  },

  onLoad(options) {
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: res => {
              this.setData({
                userInfo: res.userInfo
              })
            }
          })
        }
      }
    })
  },

  onReady:function() {
    // 监听
    chatroomCollection.watch({
      onChange: this.onChange.bind(this),
      onError(err) {
        console.error(err)
      }
    })
    const result = wx.cloud.callFunction({
      name: 'login',
      success: res => {
        console.log('[数据库] [记录openid] 成功: ', res.result.openid)
        this.setData({
          openId: res.result.openid
        })
      },
      fail: err => {
        console.log('[数据库] [查询记录] 失败: ', err)
      }
    })
  },

  onChange(snapshot) {
    console.log(snapshot)
    // 监听开始时的初始化数据
    if (snapshot.type === 'init') {
      this.setData({
        chats: [
          ...this.data.chats,
          ...[...snapshot.docs].sort((x, y) => x.sendTimeTS - y.sendTimeTS),
        ],
      })
    } else {
      const chats = [...this.data.chats]
      for (const docChange of snapshot.docChanges) {
        // queueType:列表更新类型，表示更新事件对监听列表的影响
        switch (docChange.queueType) {
          // init	初始化列表
          // update	列表中的记录内容有更新，但列表包含的记录不变
          // enqueue	记录进入列表
          // dequeue	记录离开列表
          case 'enqueue': // 记录进入列表
            chats.push(docChange.doc)
            break
        }
      }
      this.setData({
        chats: chats.sort((x, y) => x.sendTimeTS - y.sendTimeTS),
      })
    }
  },

  onGetUserInfo(e) {
    if (e.detail.userInfo) {
      this.setData({
        userInfo: e.detail.userInfo
      })
    }
  },

  onTextInput(e) {
    this.setData({
      textInputValue: e.detail.value
    })
  },

  onSend() {
    if (!this.data.textInputValue) {
      return
    }
    const doc = {
      avatar: this.data.userInfo.avatarUrl,
      nickName: this.data.userInfo.nickName,
      msgText: 'text',
      textContent: this.data.textInputValue,
      sendTime: new Date(),
      sendTimeTS: Date.now(),
    }
    chatroomCollection.add({
      data: doc,
    })
    this.setData({
      textInputValue: '',
    })
  },
})