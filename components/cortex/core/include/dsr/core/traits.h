//
// Created by juancarlos on 18/8/20.
//

#ifndef TRAITS_H
#define TRAITS_H

#include <array>
#include <cstdint>
#include <string>
#include <type_traits>
#include <vector>

namespace DSR {
    class Node;
    class Edge;
    class CRDTNode;
    class CRDTEdge;
};


template<typename T>
struct is_reference_wrapper : std::false_type {};
template<typename T>
struct is_reference_wrapper<std::reference_wrapper<T>> : std::true_type {};

template <typename T>
struct unwrap_reference_wrapper { typedef T type;  };
template <typename T>
struct unwrap_reference_wrapper<std::reference_wrapper<T>>{ typedef T type; };

template<typename T>
using unwrap_reference_wrapper_t = typename unwrap_reference_wrapper<T>::type;


template <typename T, typename ... Ts>
struct one_of
{
    static constexpr bool value = (std::is_same<std::remove_cvref_t<T>, Ts>::value || ...);
};

template<typename T>
concept allowed_types = one_of<T , int32_t, uint32_t, uint64_t,
                                   std::string, float, double,
                                   std::vector<float>, std::vector<uint8_t>,
                                   bool, std::vector<uint64_t>, std::array<float, 2>,
                                   std::array<float, 3>, std::array<float, 4>, std::array<float, 6>
                                   >::value;

template<typename Va>
concept any_node_or_edge = one_of<Va, DSR::CRDTNode, DSR::CRDTEdge, DSR::Node, DSR::Edge>::value;;

template<typename Va>
concept node_or_edge = one_of<Va, DSR::Node, DSR::Edge>::value;;


template<typename Va>
concept crdt_node_or_edge = one_of<Va, DSR::CRDTNode, DSR::CRDTNode>::value;;


//Attributes requires valid types to be defined
template<typename T>
concept AttributeType = allowed_types<unwrap_reference_wrapper_t<T>>;

//Comprueba si en el tipo T existen los attributos attr_type y attr_name
template<typename T>
concept is_attr_name = requires(T a) {
    { std::is_same_v<decltype(T::attr_type), bool> };
    { std::is_same_v<decltype(T::attr_name), std::string_view> };
    { allowed_types<unwrap_reference_wrapper_t<decltype(T::attr_type)>> };
};



#endif //TRAITS_H
