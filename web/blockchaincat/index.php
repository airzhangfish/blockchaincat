<html>
<head> 
<title>测试基于区块链的猫币</title>
<link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

</head>
<body style="margin:30px">
<?php

function http_post_json($url, $authdata, $jsonStr)
{
    $curl = curl_init(); // 启动一个 CURL 会话
    curl_setopt($curl, CURLOPT_URL, $url); // 要访问的地址
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0); // 对认证证书来源的检查
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 0); // 从证书中检查 SSL 加密算法是否存在
    curl_setopt($curl, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']); // 模拟用户使用的浏览器
    curl_setopt($curl, CURLOPT_FOLLOWLOCATION, 1); // 使用自动跳转
    curl_setopt($curl, CURLOPT_AUTOREFERER, 1); // 自动设置 Referer
    curl_setopt($curl, CURLOPT_POST, 1); // 发送一个常规的 Post 请求
    curl_setopt($curl, CURLOPT_POSTFIELDS, $jsonStr); // Post 提交的数据包
    curl_setopt($curl, CURLOPT_TIMEOUT, 30); // 设置超时限制防止死循环
    curl_setopt($curl, CURLOPT_HEADER, 0); // 显示返回的 Header 区域内容
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1); // 获取的信息以文件流的形式返回
    curl_setopt($curl, CURLOPT_HTTPHEADER, array(
            'Content-Type: application/json; charset=utf-8',
            'Content-Length: ' . strlen($jsonStr),
            'IKAAUTH: ' . $authdata,
            'PUA: ' . "HTML5"
        )
    );
    $response = curl_exec($curl);
    $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    return array($httpCode, $response, curl_error($curl));
}


?>

<h2>节点：<?php echo $_REQUEST["port"]?></h2>

<?php

//挖矿功能
if($_REQUEST["mine"]==1){
	$dataurl = 'http://localhost:'.$_REQUEST["port"].'/mine';
    $item_str = http_post_json($dataurl, "HTML5", "1");
    $item_result = json_decode($item_str[1]);
	
	echo '<h5>挖矿结果</h5>';
	var_dump($item_result->message);
}


//交易功能
if($_REQUEST["trans"]==1&&count($_REQUEST["sender"])>0&&count($_REQUEST["recipient"])>0){
	
	$transdata='{"sender":"'.$_REQUEST["sender"].'","recipient":"'.$_REQUEST["recipient"].'","amount":1,"msg":"'.$_REQUEST["sender"].' give '.$_REQUEST["recipient"].' total 1 catcoin"}';
	$dataurl = 'http://localhost:'.$_REQUEST["port"].'/trans';
    $item_str = http_post_json($dataurl, "HTML5", $transdata);
    $item_result = json_decode($item_str[1]);
	
	echo '<h5>交易结果</h5>';
	var_dump($item_result);
}

//注册节点
if($_REQUEST["reg"]==1&&count($_REQUEST["path"])>0){
	
	$transdata='{"nodes":["'.$_REQUEST["path"].'"]}';
	$dataurl = 'http://localhost:'.$_REQUEST["port"].'/nodes/register';
    $item_str = http_post_json($dataurl, "HTML5", $transdata);
    $item_result = json_decode($item_str[1]);
	echo '<h5>添加结果</h5>';
	var_dump($item_result->message);
}


//解决冲突
if($_REQUEST["reslove"]==1){
	$dataurl = 'http://localhost:'.$_REQUEST["port"].'/nodes/resolve';
    $item_str = http_post_json($dataurl, "HTML5", "1");
    $item_result = json_decode($item_str[1]);
	
	echo '<h5>同步结果</h5>';
	var_dump($item_result->message);
}



	//节点
    $dataurl = 'http://localhost:'.$_REQUEST["port"].'/nodes';
    $item_strnodes = http_post_json($dataurl, "HTML5", "1");
    $item_nodes = json_decode($item_strnodes[1]);

	//未入区块的交易
	$dataurl = 'http://localhost:'.$_REQUEST["port"].'/buftranslist';
    $item_strtrans = http_post_json($dataurl, "HTML5", "1");
    $item_trans = json_decode($item_strtrans[1]);

	//区块链
	$dataurl = 'http://localhost:'.$_REQUEST["port"].'/chain';
    $item_strchain = http_post_json($dataurl, "HTML5", "1");
    $item_chain = json_decode($item_strchain[1]);
	

    //计算每个人总共有多少猫币
	$namelist[0]='catGod';
	$namevalue[0]=0;
	foreach($item_chain->chain as $block){
		foreach($block->transactions as $transitem){
			$ishad=false;//卖家
			$count=0;
			foreach($namelist as $name){
			if($name==$transitem->sender){
				$ishad=true;
				$namevalue[$count]=$namevalue[$count]-$transitem->amount;
				break;
			}
			$count++;
			}
			if($ishad==false){
				$namelist[$count]=$transitem->sender;
				$namevalue[$count]=-$transitem->amount;
			}
			$ishad=false;//买家
			$count=0;
			foreach($namelist as $name){
			if($name==$transitem->recipient){
				$ishad=true;
				$namevalue[$count]=$namevalue[$count]+$transitem->amount;
				break;
			}
			$count++;
			}
			if($ishad==false){
				$namelist[$count]=$transitem->recipient;
				$namevalue[$count]=$transitem->amount;
			}
		}	
	}
	
	
	
	
?>

<div><a class="btn btn-primary" href="index.php?port=<?php echo $_REQUEST["port"]?>&mine=1" role="button">挖矿</a>
<a class="btn btn-primary" href="index.php?port=<?php echo $_REQUEST["port"]?>&chain=1" role="button">刷新链</a>
<a class="btn btn-primary" href="index.php?port=<?php echo $_REQUEST["port"]?>&reslove=1" role="button">多节点同步</a>
</div>
<br/>

<div>
<form class="form-inline" action="index.php?port=<?php echo $_REQUEST["port"]?>&reg=1" method="POST">
  <div class="form-group">
    <label >其他节点地址</label>
    <input type="text" class="form-control" id="path" name="path">
  </div>
  <button type="submit" class="btn btn-default">添加节点</button>
</form>
</div>
<div>
<h2>节点列表</h2>
<textarea style="width:90%;height:100px">
<?php echo $item_strnodes[1];?>
</textarea>
</div>
<div>
<form class="form-inline" action="index.php?port=<?php echo $_REQUEST["port"]?>&trans=1" method="POST">
  <div class="form-group">
    <label>卖家</label>
    <input type="text" class="form-control" id="sender" name="sender">
  </div>
  <div class="form-group">
    <label>买家</label>
    <input type="text" class="form-control" id="recipient" name="recipient">
  </div>
  <button type="submit" class="btn btn-default">确认交易</button>
</form>
</div>
<div>
<h2>总账</h2>
<?php
for($i=0;$i<count($namelist);$i++){
		echo "<br/>".$namelist[$i]."有".$namevalue[$i]."猫币";
	}
?>
</div>
<div>
<h2>尚未写入区块的交易</h2>
<textarea style="width:90%;height:200px">
<?php echo $item_strtrans[1];?>
</textarea>
</div>
<div>
<h2>区块链</h2>
<textarea style="width:90%;height:800px">
<?php echo $item_strchain[1];?>
</textarea>
</div>




</body>
</html>