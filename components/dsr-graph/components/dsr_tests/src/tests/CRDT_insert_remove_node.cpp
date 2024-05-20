//
// Created by juancarlos on 7/5/20.
//

#include <QtCore/qlogging.h>
#include <QtCore/qdebug.h>
#include "CRDT_insert_remove_node.h"
#include <thread>
#include <fstream>

void CRDT_insert_remove_node::create_or_remove_nodes(const std::shared_ptr<DSR::DSRGraph>& G)
{
    static int it=0;
    while (it++ < num_ops)
    {
        bool r = false;
        start = std::chrono::steady_clock::now();
        // ramdomly select create or remove
        if( rnd_selector() == 0)
        {
            // create node
            DSR::Node node;
            node.type("testtype");
            node.agent_id(0);
            G->add_attrib_local<name_att>(node, std::string("fucking_plane"));
            G->add_attrib_local<color_att>(node, std::string("SteelBlue"));
            G->add_attrib_local<pos_x_att>(node,  rnd_float());
            G->add_attrib_local<pos_y_att>(node,  rnd_float());
            G->add_attrib_local<parent_att>(node,  static_cast<uint64_t>(100));

            // insert node
            auto res = G->insert_node(node);
            if (res.has_value()) {
                created_nodes.push_back(res.value());
                //operations.emplace_back(Operation{0, get_unix_timestamp(), "INSERT_NODE;" + std::to_string(res.value()), true});
                qDebug() << "Created node:" << res.value() << " Total size:" << G->size();
            } else  {
                //operations.emplace_back(Operation{0, get_unix_timestamp(), "INSERT_NODE;FAIL", false});
                qDebug() << "Error inserting node "<< " Total size:" << G->size();
            }

        }
        else
        {
            //qDebug() << __FUNCTION__ << "Remove node";
            uint64_t id = removeID();
            if(id>-1)
            {
                r = G->delete_node(id);
                if (r) {
                    //operations.emplace_back(Operation{0, get_unix_timestamp(), "DELETE_NODE;" + std::to_string(id), true});
                    qDebug() << "Deleted node:" << id << " Total size:" << G->size();
                } else {
                    //operations.emplace_back(Operation{0, get_unix_timestamp(), "DELETE_NODE;FAIL(" + std::to_string(id)+ ")", false});
                    qDebug() << "Error deleting node:" << id << " Total size:" << G->size();
                }
            }
        }
        end = std::chrono::steady_clock::now();
        if (r)
            times.emplace_back(std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count());
        std::this_thread::sleep_for(std::chrono::microseconds(delay));
    }
}


void CRDT_insert_remove_node::run_test()
{
    try {
        start_global = std::chrono::steady_clock::now();
        create_or_remove_nodes(G);
        end_global = std::chrono::steady_clock::now();
        uint64_t time = std::chrono::duration_cast<std::chrono::milliseconds>(end_global - start_global).count();
        result = "CONCURRENT ACCESS: create_or_remove_nodes"+ MARKER + "OK"+ MARKER + std::to_string(time) + MARKER + "Finished properly ";
        qDebug()<< QString::fromStdString(result);

        mean = static_cast<double>(std::accumulate(times.begin(), times.end(), 0))/num_ops;
        ops_second = num_ops*1000/static_cast<double>(std::accumulate(times.begin(), times.end(), 0));
    } catch (std::exception& e) {
        std::cerr << "API TEST: TEST FAILED WITH EXCEPTION "<<  e.what() << " " << std::to_string(__LINE__) + " error file:" + __FILE__ << std::endl;
    }
}

void CRDT_insert_remove_node::save_json_result() {
    G->write_to_json_file(output);

    qDebug()<<"write results"<<QString::fromStdString(output_result);
    std::ofstream out;
    out.open(output_result, std::ofstream::out | std::ofstream::trunc);
    out << result << "\n";
    out << "ops/second"<<MARKER<<ops_second<< "\n";
    out << "mean(ms)"<<MARKER<<mean<< "\n";
    out.close();
}
