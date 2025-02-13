// 格式化 ISO 字符串为本地时间格式（zh-CN）
export const formatDate = (isoString) => {
    // 将 ISO 格式的字符串转为 Date 对象，然后使用 `toLocaleString` 格式化为本地时间
    return new Date(isoString).toLocaleString('zh-CN', {
      year: 'numeric',  // 显示年份
      month: '2-digit', // 显示月份，始终两位数字
      day: '2-digit',   
      hour: '2-digit',  
      minute: '2-digit' 
    })
  }
  
  // 截断文本，超过最大长度时添加省略号
  export const truncate = (text, maxLength) => {
    // 检查文本长度是否超过最大长度，如果超过，截取并加上省略号
    return text?.length > maxLength 
      ? text.substring(0,  maxLength) + '...'  // 截取文本并加上省略号
      : text  // 如果文本长度未超过最大长度，直接返回文本
  }
  
  // 格式化时长（以秒为单位）
  export const formatDuration = (seconds) => {
    // 如果秒数为 0 或未传入，返回 '0秒'
    if (!seconds) return '0秒'
  
    // 计算小时和分钟
    const hours = Math.floor(seconds  / 3600)  // 获取小时数
    const minutes = Math.floor((seconds  % 3600) / 60)  // 获取分钟数
  
    // 用来保存格式化后的时间部分
    const parts = []
    
    // 如果小时数大于 0，则加入小时部分
    if (hours) parts.push(`${hours} 小时`)
    
    // 如果分钟数大于 0，则加入分钟部分
    if (minutes) parts.push(`${minutes} 分钟`)
    
    // 如果既有小时又有分钟，返回小时和分钟；否则返回秒数
    return parts.join('') || `${seconds % 60}秒`
  }
  

  // 临时通知实现 
  export const useNotification = () => ({
    showError: (title, msg) => console.error(`[${title}]  ${msg}`)
  })