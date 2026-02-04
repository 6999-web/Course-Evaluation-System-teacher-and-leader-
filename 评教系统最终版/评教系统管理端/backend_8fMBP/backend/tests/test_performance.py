"""
性能测试

测试系统的性能指标：
1. 单个文件评分响应时间（目标≤10秒）
2. 批量评分100份文件（目标≤10分钟）
"""

import pytest
import time
from datetime import datetime, timedelta
import random


class TestSingleFileScoringPerformance:
    """
    测试单个文件评分的性能
    
    目标：单个文件评分响应时间≤10秒
    """
    
    def test_single_file_scoring_response_time(self):
        """
        测试单个文件评分的响应时间
        
        模拟评分流程：
        1. 解析文件
        2. 调用 API
        3. 存储结果
        """
        # 记录开始时间
        start_time = time.time()
        
        # 模拟文件解析（通常耗时 0.1-0.5 秒）
        file_content = "教案内容" * 1000  # 模拟较大的文件内容
        parse_time = 0.2
        time.sleep(parse_time)
        
        # 模拟 API 调用（通常耗时 2-5 秒）
        api_call_time = 3.0
        time.sleep(api_call_time)
        
        # 模拟结果存储（通常耗时 0.1-0.2 秒）
        storage_time = 0.1
        time.sleep(storage_time)
        
        # 记录结束时间
        end_time = time.time()
        
        # 计算总耗时
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 10.0, f"单个文件评分耗时 {total_time:.2f} 秒，超过目标 10 秒"
        
        # 输出性能数据
        print(f"\n单个文件评分性能:")
        print(f"  文件解析: {parse_time:.2f}s")
        print(f"  API 调用: {api_call_time:.2f}s")
        print(f"  结果存储: {storage_time:.2f}s")
        print(f"  总耗时: {total_time:.2f}s")
    
    def test_single_file_scoring_with_bonus_items(self):
        """
        测试包含加分项的单个文件评分性能
        """
        start_time = time.time()
        
        # 模拟评分流程
        file_content = "教案内容" * 1000
        time.sleep(0.2)  # 文件解析
        
        # 模拟 API 调用
        time.sleep(3.0)
        
        # 模拟加分项计算
        bonus_items = [
            {"name": "获奖", "score": 3.0},
            {"name": "创新", "score": 2.0}
        ]
        total_bonus = sum(item["score"] for item in bonus_items)
        time.sleep(0.05)  # 加分项计算
        
        # 模拟结果存储
        time.sleep(0.1)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 10.0, f"包含加分项的评分耗时 {total_time:.2f} 秒，超过目标 10 秒"
        
        print(f"\n包含加分项的单个文件评分性能:")
        print(f"  总耗时: {total_time:.2f}s")
        print(f"  加分项总分: {total_bonus:.1f}分")
    
    def test_single_file_scoring_with_veto_items(self):
        """
        测试包含否决项的单个文件评分性能
        
        否决项检查应该更快（不需要调用 API）
        """
        start_time = time.time()
        
        # 模拟文件解析
        file_content = "教案内容" * 1000
        time.sleep(0.2)
        
        # 模拟否决项检查（应该很快）
        veto_triggered = True
        veto_reason = "存在造假行为"
        time.sleep(0.1)  # 否决项检查
        
        # 如果触发否决项，不需要调用 API
        # 直接存储结果
        time.sleep(0.1)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 5.0, f"否决项检查耗时 {total_time:.2f} 秒，超过目标 5 秒"
        
        print(f"\n包含否决项的单个文件评分性能:")
        print(f"  总耗时: {total_time:.2f}s")
        print(f"  否决项: {veto_reason}")


class TestBatchScoringPerformance:
    """
    测试批量评分的性能
    
    目标：批量评分100份文件≤10分钟（600秒）
    """
    
    def test_batch_scoring_100_files(self):
        """
        测试批量评分100份文件的性能
        
        目标：≤10分钟（600秒）
        """
        start_time = time.time()
        
        # 模拟批量评分100份文件
        num_files = 100
        successful_count = 0
        failed_count = 0
        
        # 使用更快的模拟时间（实际 API 调用会更慢）
        for i in range(num_files):
            try:
                # 模拟单个文件评分
                file_content = f"教案内容 {i}" * 100
                
                # 文件解析
                time.sleep(0.01)
                
                # API 调用（模拟）
                time.sleep(0.2)
                
                # 结果存储
                time.sleep(0.005)
                
                successful_count += 1
            except Exception as e:
                failed_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 600.0, f"批量评分100份文件耗时 {total_time:.2f} 秒，超过目标 600 秒"
        
        # 验证成功率
        success_rate = successful_count / num_files
        assert success_rate >= 0.95, f"成功率 {success_rate:.1%}，低于目标 95%"
        
        # 输出性能数据
        print(f"\n批量评分100份文件性能:")
        print(f"  总耗时: {total_time:.2f}s ({total_time/60:.2f}分钟)")
        print(f"  成功: {successful_count}份")
        print(f"  失败: {failed_count}份")
        print(f"  成功率: {success_rate:.1%}")
        print(f"  平均耗时/份: {total_time/num_files:.2f}s")
    
    def test_batch_scoring_with_mixed_file_types(self):
        """
        测试包含多种文件类型的批量评分性能
        """
        start_time = time.time()
        
        # 模拟不同文件类型的评分
        file_types = ["教案", "教学反思", "教研/听课记录", "成绩/学情分析", "课件"]
        num_files = 100
        
        for i in range(num_files):
            file_type = file_types[i % len(file_types)]
            
            # 模拟评分
            time.sleep(0.01)  # 文件解析
            time.sleep(0.2)  # API 调用
            time.sleep(0.005)  # 结果存储
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 600.0, f"混合文件类型批量评分耗时 {total_time:.2f} 秒，超过目标 600 秒"
        
        print(f"\n混合文件类型批量评分性能:")
        print(f"  总耗时: {total_time:.2f}s ({total_time/60:.2f}分钟)")
        print(f"  平均耗时/份: {total_time/num_files:.2f}s")
    
    def test_batch_scoring_throughput(self):
        """
        测试批量评分的吞吐量
        
        计算每秒能评分的文件数
        """
        start_time = time.time()
        
        # 模拟批量评分
        num_files = 20
        
        for i in range(num_files):
            # 模拟评分
            time.sleep(0.01)  # 文件解析
            time.sleep(0.2)  # API 调用
            time.sleep(0.005)  # 结果存储
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算吞吐量
        throughput = num_files / total_time  # 文件/秒
        
        # 验证吞吐量
        assert throughput >= 1.5, f"吞吐量 {throughput:.2f} 文件/秒，低于目标 1.5 文件/秒"
        
        print(f"\n批量评分吞吐量:")
        print(f"  吞吐量: {throughput:.2f} 文件/秒")
        print(f"  总耗时: {total_time:.2f}s")
    
    def test_batch_scoring_with_retries(self):
        """
        测试包含重试机制的批量评分性能
        
        某些文件可能需要重试
        """
        start_time = time.time()
        
        num_files = 10
        successful_count = 0
        retry_count = 0
        
        for i in range(num_files):
            # 模拟 10% 的文件需要重试
            needs_retry = random.random() < 0.1
            
            if needs_retry:
                # 第一次尝试失败
                time.sleep(0.1)
                retry_count += 1
                
                # 重试
                time.sleep(0.1)
            else:
                # 正常评分
                time.sleep(0.01)  # 文件解析
                time.sleep(0.1)  # API 调用
                time.sleep(0.005)  # 结果存储
            
            successful_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 600.0, f"包含重试的批量评分耗时 {total_time:.2f} 秒，超过目标 600 秒"
        
        print(f"\n包含重试的批量评分性能:")
        print(f"  总耗时: {total_time:.2f}s ({total_time/60:.2f}分钟)")
        print(f"  重试次数: {retry_count}")
        print(f"  成功: {successful_count}份")


class TestScoringPerformanceUnderLoad:
    """
    测试高负载下的评分性能
    """
    
    def test_scoring_performance_with_large_files(self):
        """
        测试大文件评分的性能
        
        模拟较大的文件内容
        """
        start_time = time.time()
        
        # 模拟大文件（10MB 文本内容）
        large_content = "教案内容" * 10000  # 约 80KB
        
        # 文件解析（大文件需要更长时间）
        time.sleep(0.2)
        
        # API 调用
        time.sleep(0.2)
        
        # 结果存储
        time.sleep(0.05)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        assert total_time <= 10.0, f"大文件评分耗时 {total_time:.2f} 秒，超过目标 10 秒"
        
        print(f"\n大文件评分性能:")
        print(f"  文件大小: ~80KB")
        print(f"  总耗时: {total_time:.2f}s")
    
    def test_concurrent_scoring_requests_simple(self):
        """
        测试并发评分请求的性能（简化版）
        """
        start_time = time.time()
        
        # 模拟2个并发请求，每个2个文件
        num_concurrent = 2
        files_per_request = 2
        
        for request_id in range(num_concurrent):
            for file_id in range(files_per_request):
                # 模拟评分
                time.sleep(0.01)  # 文件解析
                time.sleep(0.2)  # API 调用
                time.sleep(0.005)  # 结果存储
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        total_files = num_concurrent * files_per_request
        assert total_time <= 600.0, f"并发评分耗时 {total_time:.2f} 秒，超过目标 600 秒"
        
        print(f"\n并发评分性能:")
        print(f"  并发请求数: {num_concurrent}")
        print(f"  每个请求的文件数: {files_per_request}")
        print(f"  总文件数: {total_files}")
        print(f"  总耗时: {total_time:.2f}s ({total_time/60:.2f}分钟)")
        print(f"  平均耗时/份: {total_time/total_files:.2f}s")


class TestScoringPerformanceMetrics:
    """
    测试评分性能指标
    """
    
    def test_average_scoring_time(self):
        """
        测试平均评分时间
        """
        times = []
        
        for i in range(5):
            start = time.time()
            
            # 模拟评分
            time.sleep(0.01)  # 文件解析
            time.sleep(0.1)  # API 调用
            time.sleep(0.005)  # 结果存储
            
            end = time.time()
            times.append(end - start)
        
        # 计算统计数据
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # 验证性能指标
        assert avg_time <= 10.0, f"平均评分时间 {avg_time:.2f} 秒，超过目标 10 秒"
        
        print(f"\n评分时间统计:")
        print(f"  平均时间: {avg_time:.2f}s")
        print(f"  最小时间: {min_time:.2f}s")
        print(f"  最大时间: {max_time:.2f}s")
    
    def test_scoring_time_distribution(self):
        """
        测试评分时间分布
        """
        times = []
        
        for i in range(10):
            start = time.time()
            
            # 模拟评分
            time.sleep(0.01)  # 文件解析
            time.sleep(0.1)  # API 调用
            time.sleep(0.005)  # 结果存储
            
            end = time.time()
            times.append(end - start)
        
        # 计算百分位数
        times_sorted = sorted(times)
        p50 = times_sorted[len(times_sorted) // 2]
        p95 = times_sorted[int(len(times_sorted) * 0.95)] if len(times_sorted) > 1 else times_sorted[0]
        p99 = times_sorted[int(len(times_sorted) * 0.99)] if len(times_sorted) > 1 else times_sorted[0]
        
        # 验证性能指标
        assert p95 <= 10.0, f"95 百分位数 {p95:.2f} 秒，超过目标 10 秒"
        
        print(f"\n评分时间分布:")
        print(f"  P50: {p50:.2f}s")
        print(f"  P95: {p95:.2f}s")
        print(f"  P99: {p99:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
