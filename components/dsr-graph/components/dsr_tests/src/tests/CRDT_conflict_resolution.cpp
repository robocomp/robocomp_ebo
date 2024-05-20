//
// Created by juancarlos on 7/5/20.
//

#include <QtCore/qlogging.h>
#include <QtCore/qdebug.h>
#include "CRDT_conflict_resolution.h"
#include <thread>
#include <random>
#include <fstream>

#include <type_traits>

void CRDT_conflict_resolution::insert_or_assign_attributes(const std::shared_ptr<DSR::DSRGraph>& G)
{
    static int it = 0;
    while (it++ < num_ops)
    {
        start = std::chrono::steady_clock::now();
        // request node
        std::optional<DSR::Node> node = G->get_node("world");
        if (!node.has_value())
        {
            throw std::runtime_error("ERROR OBTENIENDO EL NODO");
        }

        std::string str = std::to_string(agent_id) + "-"+ std::to_string(it);

        DSR::Attribute ab (str, 0, agent_id);
        node.value().attrs()["test_string_type"] = ab;

        G->add_or_modify_attrib_local<pos_x_att>(node.value(), rnd_float());
        G->add_or_modify_attrib_local<pos_y_att>(node.value(), rnd_float());
        bool r = G->update_node(node.value());

        if (!r) {
            throw std::runtime_error("ERROR ACTUALIZANDO EL NODO");
        }
        end = std::chrono::steady_clock::now();
        times.emplace_back(std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count());
        std::this_thread::sleep_for(std::chrono::microseconds (delay));
    }

}


void CRDT_conflict_resolution::run_test()
{
    try {
        start_global = std::chrono::steady_clock::now();
        insert_or_assign_attributes(G);
        end_global = std::chrono::steady_clock::now();
        uint64_t time = std::chrono::duration_cast<std::chrono::milliseconds>(end_global - start_global).count();
        result = "CONCURRENT ACCESS: conflict_resolution"+ MARKER + "OK"+ MARKER + std::to_string(time) + MARKER + "Finished properly ";
        qDebug()<< QString::fromStdString(result);
        mean = static_cast<double>(std::accumulate(times.begin(), times.end(), 0))/num_ops;
        ops_second = num_ops*1000/static_cast<double>(std::accumulate(times.begin(), times.end(), 0));
    } catch (std::exception& e) {
        end_global = std::chrono::steady_clock::now();
        std::string time = std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(end_global - start_global).count());
        qDebug()<< QString::fromStdString(result);
        result = "CONCURRENT ACCESS: conflict_resolution"+ MARKER + "ERROR"+ MARKER + time + MARKER + e.what();
        std::cerr << "API TEST: TEST FAILED WITH EXCEPTION "<<  e.what() << " " << std::to_string(__LINE__) + " error file:" + __FILE__ << std::endl;
    }
}

void CRDT_conflict_resolution::save_json_result() {
    G->write_to_json_file(output);

    qDebug()<<"write results"<<QString::fromStdString(output_result);
    std::ofstream out;
    out.open(output_result, std::ofstream::out | std::ofstream::trunc);
    out << result << "\n";
    out << "ops/second"<<MARKER<<ops_second<< "\n";
    out << "mean(ms)"<<MARKER<<mean<< "\n";
    out.close();
}
